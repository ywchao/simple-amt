import argparse
from collections import Counter

import simpleamt


if __name__ == '__main__':
  parser = argparse.ArgumentParser(parents=[simpleamt.get_parent_parser()])
  args = parser.parse_args()

  mtc = simpleamt.get_mturk_connection_from_args(args)

  if args.hit_ids_file is None:
    parser.error('Must specify hit_ids_file')

  with open(args.hit_ids_file, 'r') as f:
    hit_ids = [line.strip() for line in f]
  
  counter = Counter()
  min_total = float('Inf')
  num_done  = 0
  for idx, hit_id in enumerate(hit_ids):
    print 'Checking HIT %d / %d' % (idx + 1, len(hit_ids))
    hit = mtc.get_hit(hit_id)[0]
    total = int(hit.MaxAssignments)
    completed = 0
    for a in mtc.get_assignments(hit_id):
      s = a.AssignmentStatus
      #if s == 'Submitted' or s == 'Approved':
      if s == 'Submitted' or s == 'Approved' or s == 'Rejected':
        completed += 1
    counter.update([(completed, total)])
    
    if total < min_total:
        min_total = total
    
    if completed == total:
        num_done += 1

  #for (completed, total), count in counter.most_common():
  #  print '%d / %d: %d' % (completed, total, count)
  for completed in xrange(total+1):
    count = counter[(completed,total)]
    print '%d / %d: %d' % (completed, total, count)

  # show progress for extended HIT (MaxAssignments > min_total)
  #print '\n',
  for count in counter:
    if count[1] > min_total:
      print '%d / %d: %d' % (count[0], count[1], counter[(count[0],count[1])])

  # print done if all hits are done
  if num_done == len(hit_ids):
      print 'done'
