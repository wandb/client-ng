import wandb

wandb.init(project="Corona-Virus")

all_tests = {
        "6vw1": wandb.Molecule(open("../tests/fixtures/6vw1.pdb"),
            caption="Structure of 2019-nCoV chimeric receptor-binding domain complexed with its receptor human ACE2") }

wandb.log(all_tests)
