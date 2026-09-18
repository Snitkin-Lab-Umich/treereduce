import argparse
import subprocess

def parse_master_qc_file(master_qc_file):
    accession_set = set()
    with open(master_qc_file,'r') as fh:
        header = fh.readline().rstrip().split('\t')
        sample_index = header.index('Sample')
        if sample_index != 0:
            print('Warning: Sample column in unexpected location')
        for line in fh:
            accession = line.strip().split('\t')[sample_index]
            accession_set.add(accession)
    print(f'Found {len(accession_set)} accession numbers in the master QC file')
    return(accession_set)


def make_accession_list(bioproject, master_qc_file, output_file):
    # read in the master QC file and get all accession numbers in the Sample column
    accession_set = parse_master_qc_file(master_qc_file)
    # get all accession numbers from this bioproject
    temp_output_file = 'accession_list_batch_download.csv'
    # esearch -db sra -query 'PRJNA1179935' | efetch -format runinfo | cut -d ',' -f 1 >
    command = ['esearch','-db','sra','-query',bioproject,'|','efetch','-format','runinfo','|','cut','-d',',','-f','1','>',temp_output_file]
    subprocess.run(' '.join(command),shell=True)
    with open(temp_output_file,'r') as fh, open(output_file,'w') as out_fh:
        next(fh) # skip header
        out_fh.write('type\tid\ttree\n')
        for line in fh:
            line = line.rstrip()
            if not line:
                continue
            accession = line.split(',')[0]
            if accession not in accession_set:
                out_fh.write(f'run\t{accession}\tnotree\n')


def main():
    # define all args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bioproject','-b',type=str,
        help='''Provide a bioproject ID. A list of accession numbers will be generated from this bioproject.''',
        required=True
        )
    parser.add_argument(
        '--master_qc_file','-m',type=str,
        help='''Provide a path to the most recent assembly QC file with accession numbers in the Sample column. These accession numbers will not be downloaded again.''',
        required=True
        )
    parser.add_argument(
        '--output','-o',type=str,
        help='''Provide a path to an output csv file of accession numbers to download.''',
        required=True
        )
    args = parser.parse_args()
    make_accession_list(args.bioproject, args.master_qc_file, args.output)

if __name__ == "__main__":
    main()


