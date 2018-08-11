#!/bin/bash

# compute BLEU for three references only
echo "Calculating BLEU for:"

# teams participated
teams='ADAPT_Centre GKB_Unimelb PKUWriter Tilburg_University-1 Tilburg_University-2 Tilburg_University-3 UIT-DANGNT-CLNLP UPF-TALN Baseline'


for team in $teams
do
	echo $team
	tracks='all-cat old-cat new-cat MeanOfTransportation University Monument Astronaut ComicsCharacter Airport Food SportsTeam City Building Politician Athlete Artist CelestialBody WrittenWork 4size 5size 6size 7size 1size 2size 3size'
	for param in $tracks
	do
		export TEST_TARGETS_REF0=references/gold-${param}-reference0.lex
		export TEST_TARGETS_REF1=references/gold-${param}-reference1.lex
		export TEST_TARGETS_REF2=references/gold-${param}-reference2.lex
		export HYP=teams/${team}_${param}.txt
 		echo $param

		./multi-bleu.perl -lc ${TEST_TARGETS_REF0} ${TEST_TARGETS_REF1} ${TEST_TARGETS_REF2} < ${HYP} >> eval/bleu3ref-${team}_${param}.txt
		
		
	done
done

