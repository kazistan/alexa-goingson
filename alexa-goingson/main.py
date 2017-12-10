import argparse
from baydata import BAYDATA


def main():

	# Check for Command Line Arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--outdir', 
		help='output directory for data download (.csv)', type=str, 
		dest='output')
	args = parser.parse_args()

	# Invoke Bay Data
	bd = BAYDATA()
	bd.printSection(section='start')
	bd.load_all()

	# Write out
	bd.printSection(section='end', output=args.output)
	bd.write_csv(outdir=args.output)

	return 0

if __name__ == '__main__':
	main()