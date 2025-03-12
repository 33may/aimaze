for entry in *.py
do
	echo "# $entry\n $(cat $entry)\n\n" >> all_types.py
done
