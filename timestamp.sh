#!/bin/bash

while IFS=' ' read -r x; do
	echo -n `date +%d/%m/%Y\ %H:%M:%S`;
	echo -n " ";
	echo $x;
done