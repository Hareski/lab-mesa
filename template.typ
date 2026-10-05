#import "@preview/nerd-icons:0.2.0": nf-icon
#import "@preview/cetz:0.4.0"

#let corporate_color_1 = rgb("#e52713")
#let corporate_color_2 = rgb("#f69f1d")
#let corporate_color_3 = rgb("#8da6d6")
#let corporate_color_4 = rgb("#3b4395")

#let conf(title: "", subtitle: "", author: "", year: "", module: "", details: "", l: "", r: "", doc) = {
  set page(paper: "a4", margin: (x: 2.5cm, y: 2.5cm), numbering: "1 / 1")

  set page(header: [
    #grid(
      columns: (1fr, 1fr),
      align(left)[
        #if l != "" {
          text(size: 12pt, weight: "light", fill: corporate_color_3)[#r]
        } else {
          text(size: 12pt, weight: "light", fill: corporate_color_3)[INSA Lyon]
        }
      ],
      align(right)[
        #if l != "" {
          text(size: 10pt, weight: "light", fill: corporate_color_3)[#l]
        } else {
          text(size: 10pt, weight: "light", fill: corporate_color_3)[#details -- #author -- #year]
        }
      ],
    )
  ])

  show figure.caption: set text(fill: corporate_color_3.darken(30%), style: "italic")

  set text(font: "New Computer Modern", size: 11pt, lang: "fr")
  set par(justify: true, leading: 0.65em)

  set heading(numbering: "1.1")
  show heading: set text(font: "Noto Serif", weight: "semibold")
  show heading.where(level: 1): it => block[
    #text(size: 13pt, fill: corporate_color_4)[#counter(heading).display(it.numbering) -- #it.body]
  ]

  show heading.where(level: 2): it => block[
    #text(size: 11pt, font: "Noto Serif", fill: luma(20%))[#counter(heading).display(it.numbering) -- #it.body]
  ]

  show raw.where(block: true): block.with(
    fill: luma(240),
    inset: 10pt,
    radius: 4pt,
    width: 100%,
  )

  align(left)[
    #text(size: 18pt, font: "Noto Serif", weight: "semibold", fill: corporate_color_4)[#title]\
    #text(size: 12pt, font: "Noto Serif", weight: "light", fill: luma(80))[#subtitle]
  ]

  line(length: 30%, stroke: 0.5pt + gray)

  doc
}

#let call_teacher(body) = [
  #v(0.5em)
  #text(fill: rgb("#ce3000"), weight: "bold")[
    #nf-icon("nf-md-human_greeting_variant") |
  ]
  #h(0.5em)
  #text(fill: rgb("#ce3000"))[#body]
  #v(0.5em)
]

#let note(body) = [
  #block(
    fill: rgb("#e3f2fd"),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
    stroke: (left: 4pt + rgb("#2196f3")),
  )[
    #body
  ]
]

#let warn(body) = block(
  fill: rgb("#fff3e0"),
  inset: 8pt,
  radius: 4pt,
  width: 100%,
  stroke: (left: 4pt + rgb("#ff9800")),
)[
  #text(fill: rgb("#ef6c00"), weight: "bold")[#nf-icon("nf-fa-circle_exclamation") ]#body
]

#let graph_question(body) = block(
  fill: rgb("#f3e5f5"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
  stroke: (left: 4pt + rgb("#8e24aa")),
)[
  #text(fill: rgb("#8e24aa"), weight: "bold")[#nf-icon("nf-fa-chart_line")]#h(0.3em)#body
]

#let objectif(body) = block(
  fill: rgb("#e8f5e9"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
  stroke: (left: 4pt + rgb("#43a047")),
)[
  #text(fill: rgb("#43a047"), weight: "bold")[#nf-icon("nf-oct-goal")]#h(0.3em)#body
]

#let intro(body) = block(
  fill: corporate_color_3.lighten(80%),
  inset: 15pt,
  radius: 0pt,
  width: 100%,
)[

  #body
]

// Définition de la fonction exemple_box pour le contexte
#let exemple_box(title: "", body) = {
  block(
    fill: luma(245),
    stroke: (left: 4pt + eastern),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
    [
      #text(weight: "bold", fill: eastern)[#title |]
      #h(0.2em)
      #body
    ],
  )
}

#let correction(title: "Correction", body) = {
  block(
    fill: corporate_color_1.lighten(90%),
    stroke: (left: 4pt + corporate_color_1),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
    [
      #text(weight: "bold", fill: corporate_color_1)[
        #nf-icon("nf-fa-check") #h(0.3em) #title
      ]
      #v(0.5em)
      #body
    ],
  )
}

#let tp_box(title: "Travaux Pratiques", body) = {
  block(
    fill: rgb("#e0f2f1"),
    stroke: (left: 4pt + rgb("#00796b")),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
    [
      #text(weight: "bold", fill: rgb("#00796b"))[
        #nf-icon("nf-fa-laptop_code") #h(0.3em) #title
      ]
      #v(-0.2em)
      #body
    ],
  )
}

#let exo(title: none, body) = {
  block(
    fill: luma(245),
    stroke: (left: 4pt + orange.darken(20%)),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
    [
      #if title != none {
        text(weight: "bold", fill: orange.darken(20%))[#title]
        v(0.5em)
      }
      #body
    ],
  )
}

#let exercice-counter = counter("exercice")
#let question-counter = counter("question")

#let exercice(title) = context {
  exercice-counter.step()
  question-counter.update(0)
  [#text(
      size: 13pt,
      font: "Noto Serif",
      weight: "medium",
      fill: corporate_color_4,
    )[Exercice #context exercice-counter.display()  -- #title] #v(-0.7em)]
}

#let q(body) = context {
  question-counter.step()
  [#v(0.3em) #text(fill: corporate_color_4, style: "italic")[Question #context question-counter.display().] #body #v(
      0.3em,
    )]
}

#let linkwithicon(url, icon: "nf-fa-link", text_content: none) = {
  if text_content == none {
    text_content = url
  }
  link(url)[
    #text(fill: corporate_color_4)[
      #nf-icon(icon) #text_content
    ]
  ]
}

#let block_ref(body) = block(
  fill: gray.lighten(90%),
  inset: 8pt,
  radius: 4pt,
  width: 100%,
  stroke: (left: 4pt + gray),
)[
  #text(fill: gray, weight: "bold")[#nf-icon("nf-md-file_document") ]#body
]

#let answer(body, title: none) = block(
  fill: rgb("#e8f5e9"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
  stroke: (left: 4pt + rgb("#43a047")),
)[
  #if title != none {
    text(fill: rgb("#43a047"), weight: "bold")[#nf-icon("nf-oct-check") #h(0.3em) #title]
    v(0em)
  } else {
    text(fill: rgb("#43a047"), weight: "bold")[#nf-icon("nf-oct-check")]
    h(0em)
  }
  #body
]

#let adviceTeacher(body) = block(
  fill: rgb("#ffb6b6"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
  stroke: (left: 4pt + rgb("#ff0000")),
)[
  #text(fill: rgb("#ff0000"), weight: "bold")[#nf-icon("nf-oct-light_bulb")]#h(0.3em)#body
]
