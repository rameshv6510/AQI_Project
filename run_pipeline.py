import argparse, logging
from src.pipeline import run_end_to_end_pipeline
from src.demo_data import seed_demo_data
logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")
parser=argparse.ArgumentParser(description="Run the Bengaluru AQI ETL pipeline")
parser.add_argument("--days",type=int,default=14,help="Weather history days (default: 14)")
parser.add_argument("--demo",action="store_true",help="Load clearly labelled synthetic dashboard demo data instead of calling APIs")
if __name__ == "__main__":
    args=parser.parse_args()
    print(seed_demo_data(args.days) if args.demo else run_end_to_end_pipeline(args.days))
