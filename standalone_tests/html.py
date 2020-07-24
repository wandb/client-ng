import time
import numpy as np
import wandb

wandb.init(project='html-test')

N = 10

html_str = """
<marquee>W & B</marquee>
"""

all_tests = {
    "html_file": wandb.Html(open("../tests/fixtures/wb.html")),
    "html_file_seq": [wandb.Html(open("../tests/fixtures/wb.html"))],
    "html_file_str": wandb.Html(html_str),
    "html_file_str_seq": wandb.Html(html_str),
}

for i in range(0, N):
    wandb.log(all_tests, step=i)

