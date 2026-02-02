from __future__ import absolute_import
from __future__ import print_function
import os
import sys

import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

expected = """\

module top
(

);

  task automatic my_auto_task;
    input [7:0] a;
    begin
      $display(a);
    end
  endtask
  task my_simple_task;
    input [7:0] a;
    begin
      $display(a);
    end
  endtask
  task my_task_no_arg;
    begin
      $display("Hello world");
    end
  endtask

  initial begin
    my_auto_task(100);
    my_simple_task(200);
    my_task_no_arg;
  end


endmodule
"""

def test():
    # 1. Define 'task automatic my_auto_task'
    # automatic=True
    input_a = vast.Decl([vast.Input('a', width=vast.Width(vast.IntConst('7'), vast.IntConst('0')))])
    display_stmt = vast.SystemCall('display', [vast.Identifier('a')])
    task_body = [ input_a, vast.Block([vast.SingleStatement(display_stmt)]) ]

    # Note: We use the new signature for Task with 'automatic=True'
    task_auto = vast.Task('my_auto_task', task_body, automatic=True)

    # 2. Define 'task my_simple_task'
    # automatic=False (default)
    input_b = vast.Decl([vast.Input('a', width=vast.Width(vast.IntConst('7'), vast.IntConst('0')))])
    display_stmt_b = vast.SystemCall('display', [vast.Identifier('a')])
    task_body_b = [ input_b, vast.Block([vast.SingleStatement(display_stmt_b)]) ]

    task_simple = vast.Task('my_simple_task', task_body_b, automatic=False)

    # 3. Define 'task my_task_no_arg'
    # automatic=False (default)
    display_stmt_c = vast.SystemCall('display', [vast.StringConst('Hello world')])
    task_body_c = [ vast.Block([vast.SingleStatement(display_stmt_c)]) ]
    task_no_arg = vast.Task('my_task_no_arg', task_body_c, automatic=False)


    # 4. Create calls inside an Initial block
    # Call: my_auto_task(100);
    call_1 = vast.SingleStatement(
        vast.TaskCall(vast.Identifier('my_auto_task'), [vast.IntConst('100')])
    )

    # Call: my_simple_task(200);
    call_2 = vast.SingleStatement(
        vast.TaskCall(vast.Identifier('my_simple_task'), [vast.IntConst('200')])
    )

    # Call: task_no_arg();
    call_3 = vast.SingleStatement(
        vast.TaskCall(vast.Identifier('my_task_no_arg'), [])
    )

    initial = vast.Initial(vast.Block([call_1, call_2, call_3]))

    # 4. Wrap in Module
    items = [task_auto, task_simple, task_no_arg, initial]
    ast = vast.ModuleDef("top", None, None, items)

    codegen = ASTCodeGenerator()
    rslt = codegen.visit(ast)

    print(rslt)
    assert(expected == rslt)

if __name__ == '__main__':
    test()
