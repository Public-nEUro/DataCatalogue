#!/bin/bash

xlsx_dir="data_import/Aggression" 
xlsx_filename="PublicnEUro_record_Aggression.xlsx"
PNID="PN000002"

cd "import/"
python3 -c "from xlsx2jsonl import xlsx2jsonl as x2j; x2j('$xlsx_dir/$xlsx_filename')"
echo "metadata has been saved in $xlsx_dir"
python3 xlsx2xml.py $PNID $xlsx_dir/$xlsx_filename

