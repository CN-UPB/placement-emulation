# sequentially run multiple (all?) combinations of service-source on Colt
set -e

# run each placement algorithm sequentially
for ALG in bjointsp random
do
	# fw1chain
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source0.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source1.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source2.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source3.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source4.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source5.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source6.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source7.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source8.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw1chain.yaml -s inputs/sources/source9.yaml -c 100

	# fw2chain
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source0.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source1.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source2.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source3.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source4.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source5.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source6.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source7.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source8.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw2chain.yaml -s inputs/sources/source9.yaml -c 100

	# fw3chain
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source0.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source1.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source2.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source3.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source4.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source5.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source6.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source7.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source8.yaml -c 100
	./place-emu.sh -a $ALG -n inputs/networks/Colt.graphml -t inputs/services/fw3chain.yaml -s inputs/sources/source9.yaml -c 100
done

