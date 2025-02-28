#!/bin/bash

xlsx_dir="data_import/Aggression"
xlsx_f="PublicnEUro_record_Aggression.xlsx"
jsonl_f="PublicnEUro_record_Aggression.jsonl"
f_l="file_list.jsonl"
PNID="PN000002"
l2f2="PublicnEuro"
l2f3="Test_agent"

cd "import/"
python3 -c "from xlsx2jsonl import xlsx2jsonl as x2j; x2j('$xlsx_dir/$xlsx_filename')"
#echo "metadata has been saved in $xlsx_dir"

#python3 -c "from listjl2filetype import listjl2filetype as l2f; l2f('$xlsx_dir/$jsonl_f', '$xlsx_dir/$f_l', '$l2f2', '$l2f3')"
#echo "information is now added"


#python3 xlsx2xml.py $PNID $xlsx_dir/$xlsx_filename

