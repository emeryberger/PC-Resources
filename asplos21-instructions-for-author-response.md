# ASPLOS 2021 Instructions for Author Response

This document is intended to help you write the most effective author response possible.

For ASPLOS'21, the author response will not be limited in length. However, there will be a **soft limit of 500 words. Reviewers will not be required to read more than this number of words**. However, they will be interested in reading your responses to their specific questions.

**Important note: your response is not allowed to introduce new content in the paper, such as recent and improved experimental results. Your response should NOT reveal your identity or your affiliation, directly or indirectly, **as ASPLOS is a fully double-blind conference.

_Note: You will receive 5 or more reviews in the Round 2 phase. Due to circumstances beyond our control (e.g., reviewer health emergencies), there is a small number of reviews that may arrive late. Please periodically re-check the submission site during the rebuttal period. _

_Note: You may also have a few Round 1-only reviews, which have comments and questions but no score in the “R2 Overall Merit” field. This is normal — by design, there are more reviewers for extended abstracts than for the full papers. Please do answer any key questions these reviews bring up. _


## Process

All reviewers will be directed to read carefully the responses and update their reviews to take them into account, when appropriate. Reviewers will be allowed and encouraged to change their grades in light of clarifications from author responses.


## Structure

We recommend you structure your response as follows:


### First 500 Words



1. In the first 500 words of your response, you should focus on **overarching concerns** expressed by the reviewers in the “questions to the authors” section of their reviews. You should refer to them as "Reviewer A", "Reviewer B", etc.; for brevity, you can simply refer to them as "A, B". Note that you can use Markdown formatting in HotCRP, which we encourage (see below).

_Example:_


```
    # Performance Results [A, B]

    We inadvertently left off this detail of our evaluation: all reported execution times are the average of 1,024 runs, after discarding the first warm-up run. We will also report variance, which in all cases was below 0.001%.
```



### Remainder of the Response



2. In the remainder of your response, we _recommend_ that you structure your response in one of two ways: \

    1. Include responses to each individual reviewer's questions, _with the most important and most frequent questions addressed first_, as above.
    2. Alternatively, organize your response _by reviewer_. Include references to responses (when there are repeated questions) by labeling each response with a letter and number (as in, "B1"). 

_Example of approach 2b:_


```
    ## Reviewer B

    ### B1: Experimental Platform?

    To ensure repeatable runs, our experimental platform was placed in a seismically-isolated climate controlled room set at 50 degrees Fahrenheit (10 degrees Celsius, 283.15 Kelvin, -9.77 Réaumur). Hyperthreading was disabled. Background tasks were killed with extreme prejudice.

    # Reviewer C

    …

    ### C3: Experimental Platform?

See B1.
```



## Strategy

First, while writing a response is not required, it's _highly recommended_. A lack of a response is often interpreted to mean the authors implicitly admit the validity of any criticism or concerns raised by reviewers. It can quickly turn into a reason for rejection — and it almost inevitably does. A failure to write a response will almost certainly doom a paper.

Second, for the reasons given above, it's a very good idea to make sure to answer as many **important **questions as possible posed by the reviewers, especially the ones called out as "Questions to Authors" (reviewers are specifically asked to put their questions there, but sometimes the questions are also in the main comments, so make sure to look there, too!).

Third, most papers have a mix of reviews ranging from highly positive to somewhat or even quite negative. Papers generally need an enthusiastic "champion" to be accepted. You should strive to help your champion advocate for your paper (it will be obvious based on grades who this reviewer or reviewers are). Similarly, there may be detractors of your paper. Try to address their concerns factually and constructively. Ideally, you can provide compelling answers that address all their concerns so that they are no longer opposed to the paper's acceptance.

This of course doesn't mean your paper will be accepted, but it can increase the odds, especially if a detractor based their review on a misunderstanding that your response allays.


## Tone

Finally, we encourage you to be civil, polite, and constructive; your response is engaging with actual human beings. Reviewers are people too and they are genuinely interested in your responses to their questions.

It's natural to feel upset when a reviewer doesn't see the value in your paper, but no matter how wrong you believe the reviewer is, it's never a good idea to let that anger come through in a review because it absolutely won't help your paper be accepted. It could even jeopardize your paper's chances on a subsequent submission because the same reviewer might see it again and remember how rude you were. When all the reviews are negative and it's clear your paper isn't going to be accepted, a bridge-burning response can be satisfying but will do more harm than not submitting a rebuttal at all.


## Other resources

This blog post by Mike Hicks provides similar if not identical guidance and contains examples of real author responses: [http://www.pl-enthusiast.net/2014/09/17/advice-writing-author-response/](http://www.pl-enthusiast.net/2014/09/17/advice-writing-author-response/)
