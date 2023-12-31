'''

Created on Nov. 30, 2017

@author Andrew Habib

'''

import os
import sys

from collections import Counter, OrderedDict
from statistics import mean, median

from Util import load_parsed_sb, NO_WARNING

if __name__ == '__main__':
      
    sb_file = os.path.join(os.getcwd(), sys.argv[1])
    sb_res = load_parsed_sb(sb_file)
  
    proj_to_msg_count = {}
    categories = []
    for msg in sb_res:
        categories.append(msg.typ)
        
        if msg.typ == NO_WARNING:
            proj_to_msg_count[msg.proj] = 0
        else:
            try:
                proj_to_msg_count[msg.proj] += 1
            except KeyError:
                proj_to_msg_count[msg.proj] = 1
            
    print()
    print("-------------------------")
    print("Stats on warnings per bug")
    print("-------------------------")
    print()
    
    msgs_count = proj_to_msg_count.values()
    print('{:>6}: {:>4}'.format("Min", min(msgs_count)))
    print('{:>6}: {:>4}'.format("Max", max(msgs_count)))
    print('{:>6}: {:>6.2}'.format("Mean", mean(msgs_count)))
    print('{:>6}: {:>6}'.format("Median", median(msgs_count)))
    print('{:>6}: {:>4}'.format("Total", sum(msgs_count)))
    
    categories = Counter(categories)
    no_warning_count = categories[NO_WARNING]
    del categories[NO_WARNING]
    
    topX = OrderedDict(Counter(categories).most_common(5))
    max_length = max(len(i) for i in topX)
#     print('{0:-<{1}}'.format('-', max_length))
#     print('{0:^{1}}'.format("Stats per error category", max_length))
#     print('{0:-<{1}}'.format('-', max_length))
    print()
    print("------------------------")
    print("Stats per error category")
    print("------------------------")
    print()
    
    print("\n".join('{:>{}}: {:>4}'.format(i, max_length, j) for i, j in topX.items()))
    print()
    
    print('{:>{}}: {:>4}'.format("Projects without warnings", max_length, no_warning_count))
    print()