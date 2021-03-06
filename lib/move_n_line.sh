#!/bin/bash

function split_files {
    file=$1
    outputfilename=$2
    n=2000000
    if [ -n "$3" ]; then
	n=$3
    fi
    split -l $n $file $outputfilename
}
function traverse {
    path=$1
    echo 'Traversing path: $path'
    for OUTPUT in $(ls $path);
do 
	echo "***********${path}/$OUTPUT*************";
	head  $path/$OUTPUT;
	echo '**********************'; 
done
}

function traverse_and_move {
    path=$1
    echo 'Traversing path: $path'
    filefrom=''
    for OUTPUT in $(ls $path);
    do 
	fileto=$filefrom
	filefrom=$path/$OUTPUT;
	if [ -n "$fileto" ]; then
	    echo "From $filefrom to $fileto"
	    move_lines $filefrom $fileto 2
	 fi
    done
}

function delete_first_n_line {
    file=$1
    outfile=$2
    n=$3
    sed -e "1,${n}d" $file > $outfile
}

function move_lines {
   filefrom=$1
   fileto=$2
   n=$3
   tmpfile=$(date +%s)
   head -n $n $filefrom >> $fileto
   delete_first_n_line $filefrom $tmpfile $n
   mv $tmpfile $filefrom
}

echo 'usage: . move_n_line.sh'
echo ''
echo 'move_lines fromfile tofile numberoflines'
echo 'move_lines ~/Datasets/snap/splited-07/tweets2009-07-splitedag ~/Datasets/snap/splited-07/tweets2009-07-splitedaf 3'
echo ''
echo 'traverse ~/Datasets/snap/splited-07/'
echo 'traverse_and_move /home/cagil/Datasets/snap/splited/splited-09/'
echo ''
echo 'delete_first_n_line test/from.txt test/from2.txt 1'
echo ''
echo 'split_files test/from.txt test/from'

#move_lines $1 $2 $3
#traverse $1

#head -n 6 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedag > from.txt
#tail -n 5 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedaf > to.txt
#move_lines from.txt to.txt 3