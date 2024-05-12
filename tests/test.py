import init
import os
import constants

def test():
    valid = False
    path = 'subs2.srt'
    init.main(path, None)
    newFile = 'subs2_top_%s.txt' % constants.default_output_count
    if os.path.isfile(newFile):
        valid = True
        os.remove(newFile)  
    # end del-file
    assert valid
    