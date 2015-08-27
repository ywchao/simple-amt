import argparse, json
import simpleamt

if __name__ == '__main__':
  parser = argparse.ArgumentParser(parents=[simpleamt.get_parent_parser()])
  args = parser.parse_args()
  mtc = simpleamt.get_mturk_connection_from_args(args)

  approve_ids = []
  reject_ids  = []
  reject_msg  = []
  reject_hid  = []

  # load hit id file
  if args.hit_ids_file is None:
    parser.error('Must specify --hit_ids_file.')

  with open(args.hit_ids_file, 'r') as f:
    hit_ids = [line.strip() for line in f]

  # load reject file
  if args.reject_file is None:
    parser.error('Must specify --reject.')

  with open(args.reject_file, 'r') as f:
    reject = [line.strip() for line in f]

  reject_ids_all = []
  reject_msg_all = []
  for line in reject:
    reject_ids_all.append(line[0:35].strip());
    reject_msg_all.append(line[35:].strip());

  # load other parameters
  if args.reject_only is None:
    reject_only = False
  else:
    reject_only = args.reject_only

  if args.auto_mode is None:
    auto_mode = False
  else:
    auto_mode = args.auto_mode

  # get reject assignments
  for hit_id in hit_ids:
    for a in mtc.get_assignments(hit_id):
      if a.AssignmentStatus == 'Submitted':
        try:
          # Try to parse the output from the assignment. If it isn't
          # valid JSON then we reject the assignment.
          output = json.loads(a.answers[0][0].fields[0])
          if a.AssignmentId in reject_ids_all:
            idx = reject_ids_all.index(a.AssignmentId)
            msg = reject_msg_all[idx]
            reject_ids.append(a.AssignmentId)
            reject_msg.append(msg)
            reject_hid.append(hit_id)
          else:
            approve_ids.append(a.AssignmentId)
        except ValueError as e:
          reject_ids.append(a.AssignmentId)
          reject_msg.append('Invalid results')
          reject_hid.append(hit_id)

  if not reject_only:
    print ('This will approve %d assignments and reject %d assignments with '
      'sandbox=%s' % (len(approve_ids), len(reject_ids), str(args.sandbox)))
  else:
    print ('This will reject %d assignments with '
      'sandbox=%s' % (len(reject_ids), str(args.sandbox)))

  if auto_mode:
    s = 'Y'
  else:
    print 'Continue?'
    s = raw_input('(Y/N): ')
  
  if s == 'Y' or s == 'y':
    #print 'Approving assignments'
    # approve
    if not reject_only:
      for idx, assignment_id in enumerate(approve_ids):
        print 'Approving assignment %d / %d' % (idx + 1, len(approve_ids))
        mtc.approve_assignment(assignment_id)
    # reject
    for idx, assignment_id in enumerate(reject_ids):
      print 'Rejecting assignment %d / %d' % (idx + 1, len(reject_ids))
      #mtc.reject_assignment(assignment_id, feedback='Invalid results')
      mtc.reject_assignment(assignment_id, feedback=reject_msg[idx])
  else:
    print 'Aborting'


  # repost rejected assignments
  if len(reject_ids) != 0:

    if auto_mode:
      print ('Re-posting rejected assignments ...')
      s = 'Y'
    else:
      print ('Re-post rejected assignments?')
      s = raw_input('(Y/N): ')

    if s != 'N' and s != 'n':
      for idx, hit_id in enumerate(reject_hid):
        print 'Re-post HIT %s' % hit_id
        mtc.extend_hit(hit_id,1)



