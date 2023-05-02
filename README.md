# Metal2Vec

A collection of simple scripts for scraping text of metal album reviews, then using them to train a custom Word2Vec model.  We use the library gensim for training Word2Vec models.

To train a Word2Vec model, gensim requires an iterator which yields lists of tokenized words. We use NLTK for sentence and word tokenization.

<code>scrape.py</code> is a script used to scrape for metal album reviews from the website https://www.metal-archives.com, and they are subsequently stored in JSON format with additional band information.


To train a model on the scraped text, run <code>python metal2vec.py</code> (need to install libraries like gensim and NLTK), which saves the model to a file <code>metal2vec.model</code>

<code>nltk_analyze.py</code> a small separate script to bundle all the scraped review text into an NLTK Text Collection object, if we want to do simple NLTK text analysis, for example to count occurrence of words, or to examine word collocations, etc.

Once a model has been trained, we can investigate it, and see results like the following.

<code>from gensim.models import Word2Vec</code>  

<code>model = Word2Vec.load('metal2vec.model')</code>

<code>model.wv.most_similar('guitar')</code>  

<code>
[('keyboard', 0.7434054613113403),
 ('guitars', 0.6595211029052734),  
 ('organ', 0.6369956731796265),  
 ('tapping', 0.6351393461227417),  
 ('bass', 0.6217143535614014), 
 ('cello', 0.6183875799179077),  
 ('synth', 0.6144397258758545),  
 ('percussion', 0.6084404587745667),  
 ('piano', 0.6072964072227478),  
 ('drum', 0.6049701571464539)]
</code>

<code>model.wv.most_similar('thrash')</code>

<code>
[('death/thrash', 0.7642471790313721),
 ('grindcore', 0.7229084372520447),
 ('doom', 0.7182871699333191),
 ('sludge', 0.7069088220596313),
 ('melodeath', 0.6937293410301208),
 ('speed/thrash', 0.6886641979217529),
 ('nwobhm', 0.6821368336677551),
 ('prog', 0.680372953414917),
 ('metalcore', 0.6787870526313782),
 ('thrash/speed', 0.6737620830535889)]
</code>

<code>model.wv.most_similar('record')</code>

<code>
[('album', 0.9425547122955322),
 ('release', 0.813746452331543),
 ('ep', 0.7191856503486633),
 ('cd', 0.6953387260437012),
 ('lp', 0.6692390441894531),
 ('effort', 0.6583943963050842),
 ('disc', 0.6331155896186829),
 ('dvd', 0.5973551273345947),
 ('demo', 0.5813403725624084),
 ('output', 0.5806112885475159)]
</code>