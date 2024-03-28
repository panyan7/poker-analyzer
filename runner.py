import argparse
from analyzer import PokerAnalyzer


parser = argparse.ArgumentParser()
parser.add_argument("-l", "--location", type=str, default="")
parser.add_argument("-t", "--table", action="store_true")
parser.add_argument("-y", "--year", type=int, default=-1)
args = parser.parse_args()

analyzer = PokerAnalyzer()

summary_args = {}
if args.location != "":
    summary_args['location'] = args.location
if args.year != -1:
    summary_args['year'] = args.year

analyzer.summary(**summary_args)

if args.table:
    analyzer.summary_table()

