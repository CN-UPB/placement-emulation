# sequentially run all combinations of algorithm, network, service, source within the specified sets
set -e


for ALG in bjointsp random greedy
do
	for NET in Airtel BtEurope Cogentco
	do
		for SERVICE in fw1chain fw2chain fw3chain
		do
			for SRC in source0 source1 source2 source3 source4 source5 source6 source7 source8 source9
			do
				./place-emu.sh -a $ALG -n inputs/networks/$NET.graphml -t inputs/services/$SERVICE.yaml -s inputs/sources/$SRC.yaml -c 100
			done
		done
	done
done

