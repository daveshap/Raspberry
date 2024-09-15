<div align="center">

# Raspberry

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/daveshap/Raspberry?style=social)](https://github.com/daveshap/Raspberry/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/daveshap/Raspberry?style=social)](https://github.com/daveshap/Raspberry/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/daveshap/Raspberry?style=social)](https://github.com/daveshap/Raspberry/watchers)

<img src="media/think.png" alt="Think" width="100%"/>

</div>

## Mission

Create an open source toy dataset for finetuning LLMs with reasoning abilities

## Method

1. **Synthesize complex user queries:** We will start by synthesizing 500 distinct user queries across a variety of challenging domains and tasks. These user queries will require a variety of skills and abilities, such as math, coding, logic, reasoning, and planning. They will span numerous domains, from medicine and science, to software development, and other economically valuable sectors. After initial synthesis, we will use rubrics and similar grading techniques to measure and improve the samples. 
2. **Synthesize CoT and Self-Critique data:** The next phase will be to use a variety of automated prompt strategies to synthesize answers to the user queries. Models, such as Claude, have already demonstrated the ability to use CoT reasoning when correctly prompted. Furthermore, these models can self-critique and self-correct when prompted correctly.
3. **Clean and Rectify Samples:** By using rubrics and similar grading techniques, we will assess the quality of the CoT and self-critique samples. Furthermore, using a series of prompts, we will clean these samples such that they represent a singular, coherent response, thus ideal for a "single shot reasoner" dataset.
4. **Finetune an LLM with the toy dataset:** The first model will be a pilot, more of a proof of concept. We will test it and see how it performs, and iterate accordingly.
5. **Scale Up and Seek Funding:** Assuming we get acceptable results, we might try to seek funding for a larger dataset with more robust testing and benchmarking. We will need to ensure that this open source dataset covers many tasks and domains, and that it is easily usable and adaptable to multiple frameworks and architectures. Likely try and kickstart a project from Manifund. https://manifund.org/
