""" Master script to be used for making pom changes for patch and release specific tasks.
    Usage: python masterScript.py <USERID> <CODE> <!Optional:Code specific params>
    CODES:
    1: X.XX.X-SNAPSHOT to X.XX.X for master (1st task for milestone)
    2: X.XX.X to X.XX+1.X-SNAPSHOT for master (2nd pom task for milestone)
    3: X.XX.X to X.XX+1.X-SNAPSHOT for rel {PARAM: relbranch} (3rd pom task for milestone)
    4: X.XX.X-SNAPSHOT to X.XX.X+1 for rel {PARAM: relbranch} (1st pom task for patch)
    5: X.XX.X+1 to X.XX.X+1-SNAPSHOT for rel {PARAM: relbranch} (2nd pom task for patch)"""

import sys

#file imports
import milestoneRemoveSnapshot
import milestoneMasterAddSnapshotAndIncrement
import milestoneRelAddSnapshotAndIncrement
import patchRelRemoveSnapshotAndIncrement
import patchRelAddSnapshot

USERID = sys.argv[1]
CODE = sys.argv[2]

if CODE == '1':
    # X.XX.X-SNAPSHOT to X.XX.X master
    milestoneRemoveSnapshot.main(USERID)
elif CODE == '2':
    # X.XX.X to X.XX+1.X-SNAPSHOT master
    milestoneMasterAddSnapshotAndIncrement.main(USERID)
elif CODE == '3':
    # X.XX.X to X.XX+1.X-SNAPSHOT rel
    if len(sys.argv) <4:
        print("*****FAILURE*****/nScript parameters does not contain rel branch")
    else:
        RELBRANCH = sys.argv[3]
        milestoneRelAddSnapshotAndIncrement.main(USERID,RELBRANCH)
elif CODE == '4':
    # X.XX.X-SNAPSHOT to X.XX.X+1 rel
    if len(sys.argv) <4:
        print("*****FAILURE*****/nScript parameters does not contain rel branch")
    else:
        RELBRANCH = sys.argv[3]
        patchRelRemoveSnapshotAndIncrement.main(USERID,RELBRANCH)
elif CODE == '5':
    # X.XX.X+1 to X.XX.X+1-SNAPSHOT rel
    if len(sys.argv) <4:
        print("*****FAILURE*****/nScript parameters does not contain rel branch")
    else:
        RELBRANCH = sys.argv[3]
        patchRelAddSnapshot.main(USERID,RELBRANCH)
else:
    print("Incorrect CODE")
