import wandb

N = 1

all_tests = {
    "6vw1": wandb.Molecule(open("tests/fixtures/3EVP.pdb"),
        caption="Structure of 2019-nCoV chimeric receptor-binding domain complexed with its receptor human ACE2")
}

if __name__ == "__main__":
    wandb.init(project="Corona-Virus")

    for i in range(0, N):
        wandb.log(all_tests)
