# You Can Code Gen AI Apps: Code Your First Smart Writing Assistant (Without Spending a Cent) ✨

source: [You Can Code Gen AI Apps: Code Your First Smart Writing Assistant (Without Spending a Cent) by Jannis Douloumis](https://medium.com/@PowerUpSkills/you-can-code-gen-ai-apps-code-your-first-smart-writing-assistant-without-spending-a-cent-029df71f75f9)


*How I went from avoiding AI development to building something actually useful in just 2 hours — and you can too*

**The Confession: I Was Scared of Gen AI**

Let me be brutally honest with you. One year ago, I was that a technical product owner in a developer team who scrolled past every “Build with AI” tutorial, convinced I needed:

  * A computer science PhD to understand transformers
  * Thousands of dollars for GPU credits
  * Months of study before I could build anything useful
  * Some mysterious “AI intuition” that I clearly lacked

Sound familiar?

I kept seeing colleagues casually dropping terms like “transformers,” “HuggingFace,” and “fine-tuning” in Slack, while I nodded along pretending I knew what they meant. The breaking point came during a sprint planning meeting when our PM asked, “Can we add some AI features?” and everyone looked at me. The silence was deafening.

That weekend, I decided enough was enough. I was going to crack this Gen AI barrier once and for all.

**Spoiler alert**: By Sunday evening, I had built a smart writing assistant that my non-technical friends were actually impressed by. And it cost me exactly $0.

You can download my project code from github:

[**GitHub - PowerUpSkills/my-first-ai-assistant: A simple Python AI text generation application using…**](https://github.com/PowerUpSkills/my-first-ai-assistant?source=post_page-----029df71f75f9---------------------------------------)
[A simple Python AI text generation application using Hugging Face Transformers and GPT-2 …](https://github.com/PowerUpSkills/my-first-ai-assistant?source=post_page-----029df71f75f9---------------------------------------)

[github.com](https://github.com/PowerUpSkills/my-first-ai-assistant?source=post_page-----029df71f75f9---------------------------------------)

**Step 1: Admitting My Assumptions Were Wrong**

First, I had to confront my biggest misconceptions:

**❌ Myth**: “I need expensive GPU access to run AI models”

**✅ Reality**: Most smal pre-trained models run fine on my MacBook Pro M1

**❌ Myth**: “I need to understand the math behind transformers”

**✅ Reality**: I can use them effectively without knowing every equation

**❌ Myth**: “Building something useful takes weeks”

**✅ Reality**: I had a working prototype in 2 hours

**❌ Myth**: “I need to pay for API credits”

**✅ Reality**: Open-source models are completely free

The breakthrough moment? Realizing that using transformers is like using any other library — I don’t need to understand how React renders virtual DOM to build great UIs.

*Transformers are neural network architectures that are crucial in generative AI (GenAI), enabling models like GPT (Generative Pre-trained Transformer) to generate human-like text.*

**Step 2: Setting Up My “AI Lab” (15 Minutes)**

Here’s exactly what I did, step by step:

**My Setup**

  * **Computer**: 2019 MacBook Pro (nothing fancy)
  * **Editor**: VS Code (already installed)
  * **Total cost**: $0

**The 15-Minute Installation**

```
\# Create my first AI project
mkdir my-first-ai-assistant
cd my-first-ai-assistant
code .
```

I created a simple requirements.txt:

```
transformers>=4.30.0
torch>=2.0.0
numpy
```

Then installed everything:

```
pip install -r requirements.txt
```

The installation downloads about 500MB of dependencies. Not huge, but I made coffee while it ran.

**Step 3: My First “Holy Shit, It Actually Works” Moment**

I started with the absolute simplest code possible. No complex architectures, no custom training — just pure copy-paste to see if anything would happen:

```
\# my_first_ai.py
from transformers import pipeline


\# This felt like magic
generator = pipeline("text-generation", model="gpt2")


\# My test
prompt = "The best thing about being a developer is"
result = generator(prompt, max_length=50)
print(result['generated_text'])
```

I hit Enter, and waited. My terminal showed some downloading progress bars, then:

```
The best thing about being a developer is the ability to create something
from nothing, to solve complex problems with elegant code,
and to constantly learn new technologies that shape the future.
```

**I literally stared at my screen for 30 seconds.**

This simple script had just generated coherent, contextually relevant text. **No API keys, no cloud credits, no PhD required. Just 5 lines of Python.**

**Step 4: Building Something Actually Useful**

Feeling confident, I decided to build something my non-technical friends would find impressive: a smart writing assistant. This time we even have an option to choose from more advanced huggingface provided models.

**The Interactive Writing Buddy**

```python
\# smart_writer.py
from transformers import pipeline
import re

class ImprovedWritingAssistant:
   def __init__(self, model_name="distilgpt2"):
       print("🤖 Starting up your improved AI writing buddy...")
       print(f"📦 Using model: {model_name}")

       \# Model options with descriptions
       model_info = {
           "gpt2": "Original GPT-2 (500MB, basic quality)",
           "distilgpt2": "DistilGPT-2 (350MB, faster, often better)",
           "gpt2-medium": "GPT-2 Medium (1.5GB, better quality)",
           "gpt2-large": "GPT-2 Large (3GB, best quality)"
       }

       if model_name in model_info:
           print(f"ℹ️  {model_info[model_name]}")

       try:
           self.generator = pipeline(
               "text-generation",
               model=model_name,
               max_length=120
           )
           print("✅ Ready to help with better writing!")
       except Exception as e:
           print(f"⚠️  Could not load {model_name}, falling back to GPT-2")
           self.generator = pipeline(
               "text-generation",
               model="gpt2",
               max_length=120
           )
           print("✅ Ready to help with basic writing!")

   def clean_output(self, text, max_length=200):
       """Clean and limit the generated text"""
       \# Remove extra whitespace and newlines
       text = ' '.join(text.split())

       \# Split into sentences
       sentences = re.split(r'[.!?]+', text)

       \# Take first few complete sentences
       result = ""
       for sentence in sentences[:3]:
           sentence = sentence.strip()
           if len(sentence) > 10 and len(result + sentence) < max_length:
               result += sentence + ". "

       return result.strip() if result else text[:max_length] + "..."

   def brainstorm_ideas(self, topic):
       """Generate ideas with improved prompts and cleaning"""

       \# Better structured prompts
       prompts = [
           f"Mac productivity tip: Use",
           f"To improve {topic}, try",
           f"Quick {topic} hack:"
       ]

       ideas = []
       for prompt in prompts:
           try:
               result = self.generator(
                   prompt,
                   max_length=80,
                   temperature=0.6,  \# Lower temperature for more focused output
                   do_sample=True,
                   pad_token_id=50256
               )

               generated_text = result['generated_text']
               clean_text = self.clean_output(generated_text)
               ideas.append(clean_text)

           except Exception as e:
               ideas.append(f"Could not generate idea: {str(e)}")

       return ideas

   def get_curated_tips(self, topic):
       """Provide curated tips as fallback"""
       mac_tips = {
           "productivity hacks on a mac": [
               "Use Spotlight Search (Cmd+Space) to quickly find anything on your Mac",
               "Set up Hot Corners in System Preferences for instant access to features",
               "Use Mission Control (F3) to organize multiple desktops and windows",
               "Master keyboard shortcuts: Cmd+Tab (app switcher), Cmd+` (window switcher)",
               "Install Alfred or Raycast for advanced automation and quick actions"
           ],
           "mac workflow
```
