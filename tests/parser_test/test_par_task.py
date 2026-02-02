from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import tempfile
from pyverilog.vparser.parser import VerilogCodeParser

try:
    from StringIO import StringIO
except:
    from io import StringIO

# We will write this content to a temp file to parse it
verilog_code = """
module top;
  // Test automatic task definition
  task automatic my_auto_task;
    input a;
    begin
       $display(a);
    end
  endtask

  // Test normal task definition
  task my_task;
    input a;
    begin
       $display(a);
    end
  endtask

  // Test task without argument
  task my_task_no_arg;
    begin
      $display("Hello world");
    end
  endtask

  // Test task calls
  initial begin
    my_auto_task(1);
    my_task(2);
    my_task_no_arg();
  end
endmodule
"""

# Expected AST Output
# Note: Task nodes now show 'automatic=True/False' because we added it to attr_names
expected = """\
Source:  (at 2)
  Description:  (at 2)
    ModuleDef: top (at 2)
      Paramlist:  (at 0)
      Portlist:  (at 2)
      Task: my_auto_task, True (at 4)
        Decl:  (at 5)
          Input: a, False (at 5)
        Block: None (at 6)
          SingleStatement:  (at 7)
            SystemCall: display (at 7)
              Identifier: a (at 7)
      Task: my_task, False (at 12)
        Decl:  (at 13)
          Input: a, False (at 13)
        Block: None (at 14)
          SingleStatement:  (at 15)
            SystemCall: display (at 15)
              Identifier: a (at 15)
      Task: my_task_no_arg, False (at 20)
        Block: None (at 21)
          SingleStatement:  (at 22)
            SystemCall: display (at 22)
              StringConst: Hello world (at 22)
      Initial:  (at 27)
        Block: None (at 27)
          SingleStatement:  (at 28)
            TaskCall:  (at 28)
              Identifier: my_auto_task (at 28)
              IntConst: 1 (at 28)
          SingleStatement:  (at 29)
            TaskCall:  (at 29)
              Identifier: my_task (at 29)
              IntConst: 2 (at 29)
          SingleStatement:  (at 30)
            TaskCall:  (at 30)
              Identifier: my_task_no_arg (at 30)
"""

def test():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as tmp:
        tmp.write(verilog_code)
        tmp_path = tmp.name

    try:
        filelist = [tmp_path]
        parser = VerilogCodeParser(filelist)
        ast = parser.parse()

        output = StringIO()
        ast.show(buf=output)
        rslt = output.getvalue()

        print(rslt)
        assert(expected.strip() in rslt.strip())
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == '__main__':
    test()
