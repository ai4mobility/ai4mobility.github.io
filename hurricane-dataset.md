(hurricane-dataset)=
# Course Dataset: Florida Hurricane Transportation Posts

<section class="resource-hero">
  <div class="resource-eyebrow">USF &middot; AI for Mobility &middot; Course dataset</div>
  <h2>Hurricane Transportation Posts <span>Helene and Milton, 2024</span></h2>
  <p>2,425 real posts from X (Twitter) about roads, bridges, evacuation traffic, fuel, transit and airports during Hurricanes Helene and Milton, each with the images its author attached. Two views of the same moment, the words and the pixels, for text models, image models and models that combine the two.</p>
  <div class="resource-meta">
    <span>2,425 posts &middot; 3,348 images</span>
    <span>Download on Canvas only</span>
    <span>Last updated: October 2026</span>
  </div>
</section>

<div class="resource-callout">
  <p><strong>Where to get it.</strong> The data files are <strong>not</strong> on this website. Students enrolled in CGN 6933 download <code>hurricane_transport_posts_v2.zip</code> (177&nbsp;MB) from the course Canvas site, which needs a USF login. This page describes what is in the zip, how it was built, and what to watch out for before you model it.</p>
</div>

When Hurricanes Helene and Milton hit Florida in the fall of 2024, residents, cities, FDOT, transit
agencies and newsrooms posted about closed bridges, flooded roads, evacuation traffic and empty gas
pumps, and they usually attached a picture. This dataset collects **2,425 of those posts**, each with
the images its author attached.

Every post gives you **two views of the same moment: the words and the pixels**. That is what you
need to try a text encoder (BERT, {doc}`2.5 <module2/notes5-bert>`), an image encoder (ViT, CLIP,
{doc}`2.7 <module2/notes7-vision>`), and models that combine the two on the same items, and to ask
a question an agency would care about: *when does the picture tell you something the words do not?*

```{figure} _static/figures/HT_Dataset_Examples.jpg
:alt: Eight example posts, each with its image, post ID, storm, time window and automatic image label, and the start of its text. Top row, four photos: a gas pump with a sign saying 87 and 89 octane are out (HT0109); Manasota Key Road washed out beside the beach (HT0628); a traffic camera on northbound I-75 during the Milton evacuation (HT1501); a traffic camera on I-275 at the Howard Frankland Bridge with construction barges moored for the storm (HT1629). Bottom row: a "Traffic light out? Treat it as a 4-way stop" graphic (HT0470); a "Tolls suspended" graphic from the Tampa Hillsborough Expressway Authority (HT1084); a Jacksonville Transportation Authority bus with a "Detour" banner (HT2048); and an FDOT/511 map of a closed section of Dunlawton Avenue with its detour (HT2204), which the automatic label wrongly calls a graphic.
:width: 100%

Eight of the 2,425 posts. Some images show what the text says, many repeat the text as a graphic,
and some add what the text never mentions.
```

<section class="resource-section" id="at-a-glance">
  <div class="resource-section-header">
    <h2>At a Glance</h2>
    <span>Sept 20 &ndash; Oct 26, 2024</span>
  </div>
  <div class="practice-table-wrap">
    <table class="practice-table">
      <thead>
        <tr><th style="width:24%">Count</th><th>What it is</th></tr>
      </thead>
      <tbody>
        <tr><td><strong>2,425</strong> posts</td><td>Original posts (no reposts or replies), each with 1&ndash;4 images</td></tr>
        <tr><td><strong>3,348</strong> images</td><td>Resized to at most 512 px on the long side, metadata removed</td></tr>
        <tr><td><strong>1,146</strong> accounts</td><td>Residents, cities and counties, FDOT, transit agencies, airports, newsrooms</td></tr>
        <tr><td><strong>1,039</strong> / <strong>1,386</strong></td><td>Posts directly / indirectly about transportation (<code>transport_relevance</code>)</td></tr>
      </tbody>
    </table>
  </div>
</section>

<div class="placeholder-panel">
  <p><strong>Terms of use.</strong> Use the files only for CGN 6933 coursework (exercises, assignments and your class project), on your own device, your own Google Drive or Colab. Do not redistribute them: no public GitHub, Kaggle, Hugging Face or shared drives &mdash; publish your code and results, not the data. These were public posts, but their authors did not write them for this class: do not search for the original posts or try to identify anyone. If you find anything that looks like personal information or inappropriate content, stop and tell the instructor. Delete your copy at the end of the semester.</p>
</div>

## Getting started

Unzip the file from Canvas and you get one folder:

```text
hurricane_transport_posts/
  posts.csv      one row per post, 2,425 rows, 29 columns
  images/        HT0001_1.jpg ... HT2425_1.jpg  (3,348 images)
  index.html     open in your browser to scroll and filter every post with its images
  README.md      the full data card: every column, how the data was built, every caveat
```

**Look before you model.** Open `index.html` from the unzipped folder. Filter by storm, time window,
image kind and relevance, or search the text for *bridge*, *I-75*, *fuel* or *bus*. Ten minutes of
browsing will tell you more about this data than any summary table.

**Load it in Colab.** Put the zip in your Google Drive once, then:

```ipython
from google.colab import drive
drive.mount('/content/drive')
!unzip -q "/content/drive/MyDrive/hurricane_transport_posts_v2.zip" -d /content

import pandas as pd
from PIL import Image
folder = "/content/hurricane_transport_posts/"
df = pd.read_csv(folder + "posts.csv")
row = df.iloc[0]
print(row.text)
images = [Image.open(folder + p) for p in row.image_files.split(";")]   # all images of the post
Image.open(folder + row.image_file)                                     # show the first one
```

On your own laptop, skip the first three lines and set `folder` to wherever you unzipped it.

## What is in it

Helene made landfall near Perry around 11:10 p.m. EDT on September 26; Milton near Siesta Key around
8:30 p.m. EDT on October 9. Each post falls in one time window:

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:44%">Storm, window</th><th>Posts</th><th>Photos</th><th>Graphics</th><th>Maps</th></tr>
    </thead>
    <tbody>
      <tr><td>Helene, pre-landfall (Sept 20&ndash;25)</td><td>285</td><td>51</td><td>88</td><td>146</td></tr>
      <tr><td>Helene, landfall and after (Sept 26 &ndash; Oct 1)</td><td>457</td><td>192</td><td>143</td><td>122</td></tr>
      <tr><td>Milton, pre-landfall (Oct 2&ndash;8)</td><td>872</td><td>191</td><td>326</td><td>355</td></tr>
      <tr><td>Milton, landfall and after (Oct 9&ndash;17)</td><td>762</td><td>331</td><td>268</td><td>163</td></tr>
      <tr><td>Milton, late aftermath (Oct 18&ndash;26)</td><td>49</td><td>23</td><td>20</td><td>6</td></tr>
      <tr><td><strong>All</strong></td><td><strong>2,425</strong></td><td><strong>788</strong></td><td><strong>845</strong></td><td><strong>792</strong></td></tr>
    </tbody>
  </table>
</div>

Photo / graphic / map is an automatic guess on each post's first image (column `image_kind_auto`).
Windows are calendar days in UTC.

<h3 class="resource-subhead">The columns you will use most</h3>

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:36%">Column</th><th>What it holds</th></tr>
    </thead>
    <tbody>
      <tr><td><code>post_id</code></td><td><code>HT0001</code>&ndash;<code>HT2425</code>, in time order</td></tr>
      <tr><td><code>storm</code>, <code>window</code></td><td>Helene or Milton; <code>pre_landfall</code>, <code>landfall_and_after</code> or <code>late_aftermath</code></td></tr>
      <tr><td><code>hours_from_landfall</code>, <code>before_landfall</code></td><td>Exact timing against that storm's landfall (negative = before)</td></tr>
      <tr><td><code>text</code></td><td>The post, with <code>@USER</code> and <code>HTTPURL</code> in place of account handles and links</td></tr>
      <tr><td><code>image_file</code>, <code>image_files</code></td><td>The first image, and all images separated by <code>;</code></td></tr>
      <tr><td><code>image_kind_auto</code></td><td><code>photo</code>, <code>graphic</code> or <code>map</code>: a CLIP guess, not checked by a person</td></tr>
      <tr><td><code>transport_relevance</code>, <code>relevance_source</code></td><td><code>direct</code> or <code>indirect</code>, and how that was judged (see below)</td></tr>
      <tr><td><code>author_id</code>, <code>lookalike_group</code></td><td>A random code per account, and a shared code for posts whose images look nearly identical. Use both when you split train and test</td></tr>
    </tbody>
  </table>
</div>

The README in the zip describes all 29 columns, including engagement counts, keyword topics and
Brandwatch's sentiment label.

## How it was built

The source is a Brandwatch export of Florida-located X posts. Each step kept fewer posts:

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:70%">Step</th><th>Posts left</th></tr>
    </thead>
    <tbody>
      <tr><td>All unique posts, Sept 20 &ndash; Oct 26</td><td>969,867</td></tr>
      <tr><td>Originals only (no reposts, replies or quotes)</td><td>129,911</td></tr>
      <tr><td>&hellip; with at least one image</td><td>45,106</td></tr>
      <tr><td>&hellip; whose text has a transportation word (road, bridge, I-##, traffic, evacuat-, fuel, airport, bus, FDOT, &hellip;)</td><td>3,573</td></tr>
      <tr><td>Repeated images and identical texts removed; images no longer online dropped; sexual or spam content removed</td><td>3,419</td></tr>
      <tr><td><strong>Read and judged to be about transportation</strong></td><td><strong>2,425</strong></td></tr>
    </tbody>
  </table>
</div>

The last step matters. The keyword filter alone let in a lot that has nothing to do with
transportation: high-school teams playing *on the road*, a *donation drive*, a *long road to
recovery*, automated river warnings named after the highway bridge where the gauge sits. So every
post's text was read and labeled `direct`, `indirect` or `not` about transportation, and the 994
`not` posts were removed. **That reading was done by an AI model (Claude), from the text only.** An
independent second pass on 100 posts agreed on 85 of the labels. The 196 posts marked
`relevance_source = text_and_image` were also reviewed with their images and are the most carefully
labeled subset.

Account handles became `@USER`, links became `HTTPURL`, author names became random codes, and images
were shrunk to 512 px with their metadata removed. No links to the original posts are included.

## Six things that will bite you

1. **The labels are weak.** `transport_relevance` is an AI's reading of the text, `image_kind_auto`
   is CLIP's guess, `bw_sentiment` is Brandwatch's own text model. They are good enough to filter on
   or to start with. They are not ground truth, and a model that "beats" them may only have learned
   their mistakes.
2. **A few accounts post a lot.** One account has 68 posts, two others 40 and 35, and agencies reuse
   the same templates. **Split train and test by `author_id`** and keep each `lookalike_group` on one
   side, or your test set will be full of near-copies of your training set.
3. **The window is not the landfall.** The "landfall and after" window starts the day before
   landfall: 246 of Helene's 457 and 310 of Milton's 762 posts in that window were written *before*
   landfall. If your question is before vs. after, use `before_landfall`.
4. **Most images are not photos.** About two thirds are graphics or maps, and many graphics are the
   post's text again, rendered as pixels. A model that can read printed words (CLIP) will look much
   smarter on these than one that cannot (a ViT trained on ImageNet). Report photos and graphics
   separately.
5. **A picture is not proof.** Old photos from earlier storms, photos from other states, screenshots
   of TV and apps, and memes all appear. The image is what the author chose to attach.
6. **This is not a sample of hurricane Twitter.** It is a keyword-filtered slice of an export that was
   capped near 50,000 posts per time block. Never quote a percentage from it as a fact about how
   Floridians posted during the storms.

## What you can do with it

You may use this dataset in this course's exercises and in your class project. A few questions it can
answer, matched to what the course covers:

<div class="practice-table-wrap">
  <table class="practice-table">
    <thead>
      <tr><th style="width:22%">Course topic</th><th>Try this</th></tr>
    </thead>
    <tbody>
      <tr><td>Tokens</td><td><code>bert-base-uncased</code> splits <em>impassable</em> into <code>imp</code> &middot; <code>##ass</code> &middot; <code>##able</code> and <em>#HurricaneMilton</em> into <code>#</code> &middot; <code>hurricane</code> &middot; <code>##mi</code> &middot; <code>##lton</code>. What happens to <em>I-275</em>, <em>SR-60</em> or <em>Howard Frankland</em>, and does a tokenizer trained on tweets do better?</td></tr>
      <tr><td>BERT on text</td><td>Predict <code>before_landfall</code> or <code>transport_relevance</code> from the text alone. Run a TF-IDF + logistic regression baseline first, split by author.</td></tr>
      <tr><td>ViT and CLIP on images</td><td>Embed the images with a ViT trained on ImageNet and with CLIP's image encoder. Pick a flooded-road photo and compare its nearest neighbours in the two spaces. Which one groups images by object, and which by event?</td></tr>
      <tr><td>Multimodal fusion</td><td>Does adding the image improve a text-only classifier? Check photos and graphics separately, because the answer is probably different.</td></tr>
      <tr><td>Cross-attention</td><td>Hide the pairing and ask a model to find each post's own image among 100. Compare a dual encoder (CLIP) with a model whose words cross-attend to the image patches (BLIP).</td></tr>
      <tr><td>Class project</td><td>A triage tool that flags posts reporting a road condition (flooding, closure, debris, signals out) for a traffic management center, evaluated on an author-and-lookalike split.</td></tr>
    </tbody>
  </table>
</div>

<div class="resource-callout">
  <p><strong>Questions about the data?</strong> Post them on the course discussion board in Canvas so everyone sees the answer, or bring them to office hours (Tuesdays 3&ndash;5 pm, CUTR 231). If something in the files looks wrong, note the <code>post_id</code>.</p>
</div>
