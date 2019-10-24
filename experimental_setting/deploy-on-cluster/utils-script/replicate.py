import os
import sys

if len(sys.argv) != 4:
    print("Usage: script.py <script-to-replicate> <outputfolder> <times>")
    sys.exit(-1)

to_replicate = sys.argv[1]
output_folder = sys.argv[2]

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

times = int(sys.argv[3])


with open(to_replicate) as file:
	content = file.read()

for i in range(times):
	new_content = content.replace('/x', '/' + str(i))
	new_content = new_content.replace('-x', '-' + str(i))
	base=os.path.basename(to_replicate)
	filename = os.path.splitext(base)[0]
	output_path = "{0}/{1}_{2}.sh".format(output_folder, filename, str(i))
	with open(output_path, 'w') as ofile:
		ofile.write(new_content)

