class DesignSpec {
  summary string
  screens Screen[]
}

class Screen {
  name string
  description string
  wireframe string   // Markdown, HTML, or text representation
  components Component[]
}

class Component {
  name string
  description string
  code_snippet string
  notes string
}
