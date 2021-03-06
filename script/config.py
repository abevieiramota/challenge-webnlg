SUBMISSIONS_FILEPATHS = [
        '../data/webnlg2017/submissions/adaptCenter/ADAPTcentreWebNLGsubmission.txt',
        '../data/webnlg2017/submissions/melbourne/final_result.txt',
        '../data/webnlg2017/submissions/pkuwriter/PKUWriter_results.txt',
        '../data/webnlg2017/submissions/tilburg/nmt_test.out.ordered',
        '../data/webnlg2017/submissions/tilburg/smt_test.out.ordered',
        '../data/webnlg2017/submissions/tilburg/template_test.out.ordered',
        '../data/webnlg2017/submissions/uit-danglt-clnlp/Submission-UIT-DANGNT-CLNLP.txt',
        '../data/webnlg2017/submissions/upf/UPF_All_sent_final.txt',
        '../data/webnlg2017/submissions/baseline_sorted.txt'
]

CATEGORIES = ['Airport', 'Astronaut', 'Building', 'City', 'ComicsCharacter', 
              'Food', 'Monument', 'SportsTeam', 'University', 'WrittenWork']

DATASETS_FILEPATHS = {
        'dev': [
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_ComicsCharacter_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_WrittenWork_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_Astronaut_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_SportsTeam_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_Building_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_University_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_City_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_Monument_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_Airport_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/1triples/1triple_allSolutions_Food_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_Astronaut_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_University_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_SportsTeam_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_ComicsCharacter_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_Monument_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_Building_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_WrittenWork_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_Food_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/2triples/2triples_Airport_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/7triples/7triples_Monument_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/7triples/7triples_Astronaut_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/7triples/7triples_University_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/6triples/6triples_Monument_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/6triples/6triples_Astronaut_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/6triples/6triples_University_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_Airport_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_Food_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_University_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_ComicsCharacter_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_Astronaut_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_Monument_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_SportsTeam_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_Building_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/4triples/4triples_WrittenWork_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_Astronaut_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_Building_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_ComicsCharacter_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_Airport_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_SportsTeam_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_WrittenWork_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_Monument_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_University_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/5triples/5triples_Food_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_ComicsCharacter_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_University_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_Airport_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_Astronaut_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_Food_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_Building_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_Monument_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_WrittenWork_dev_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/dev/3triples/3triples_SportsTeam_dev_challenge.xml'
                ],
        'train': [
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_Airport_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_City_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_ComicsCharacter_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_Building_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_WrittenWork_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_Food_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_SportsTeam_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_Astronaut_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_Monument_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/1triples/1triples_University_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_Airport_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_ComicsCharacter_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_Astronaut_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_Food_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_Monument_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_SportsTeam_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_WrittenWork_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_Building_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/2triples/2triples_University_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/7triples/7triples_University_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/7triples/7triples_Monument_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/7triples/7triples_Astronaut_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/6triples/6triples_University_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/6triples/6triples_Monument_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/6triples/6triples_Astronaut_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_Food_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_WrittenWork_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_SportsTeam_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_Monument_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_Building_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_ComicsCharacter_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_University_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_Astronaut_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/4triples/4triples_Airport_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_University_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_Monument_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_Food_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_Astronaut_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_WrittenWork_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_Building_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_Airport_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_ComicsCharacter_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/5triples/5triples_SportsTeam_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_Food_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_Monument_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_Building_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_Astronaut_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_SportsTeam_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_ComicsCharacter_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_Airport_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_University_train_challenge.xml',
                '../data/webnlg2017/challenge_data_train_dev/train/3triples/3triples_WrittenWork_train_challenge.xml'
                ],
        'test_no_lex': ['../data/webnlg2017/testdata_no_lex.xml'],
        'test_unseen_with_lex': ['../data/webnlg2017/testdata_unseen_with_lex.xml'],
        'test_with_lex': ['../data/webnlg2017/testdata_with_lex.xml'],
        'dev_1.2': [
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/City.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/1triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/2triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/7triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/7triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/7triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/6triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/6triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/6triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/4triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/5triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/dev/3triples/SportsTeam.xml'
        ],
        'train_1.2': [
                '../../webnlg/data/delexicalized/v1.2/train/1triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/City.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/train/1triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/train/2triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/train/7triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/train/7triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/train/7triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/train/6triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/train/6triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/train/6triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/train/4triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/WrittenWork.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/train/5triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/Food.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/Monument.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/Building.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/Astronaut.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/SportsTeam.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/ComicsCharacter.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/Airport.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/University.xml',
                '../../webnlg/data/delexicalized/v1.2/train/3triples/WrittenWork.xml'
        ]
}