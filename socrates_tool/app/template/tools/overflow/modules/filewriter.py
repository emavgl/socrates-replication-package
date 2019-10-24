import os


def write_z3_script(output_folder, function_name, generated_z3) -> str:

	# Create output folder if it does not exists
	create_dir(output_folder)

	# Read static parts of the generated file
	with open('./tools/overflow/resources/top_template.txt', 'r') as template_file:
		top_template = template_file.read()

	with open('./tools/overflow/resources/bottom_template.txt', 'r') as template_file:
		bottom_template = template_file.read()

	# Write
	file_name = '{}_z3.py'.format(function_name)
	file_path = '{}/{}'.format(output_folder, file_name)
	file_content = top_template + generated_z3 + bottom_template

	with open(file_path, 'w') as output_file:
		output_file.write(file_content)

	return file_path


def create_dir(dir_path):
	# Create output folder if it does not exists
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
