# 🎓 RDF Learning Journey - PerinatalKG

## 📅 Week 1 - Day 5 (29 Apr 2026)

### ✅ O que aprendi hoje:

1. **RDF é baseado em TRIPLAS:**
   - Sujeito → Predicado → Objeto
   - Exemplo: `Clarimar → trabalha_em → PerinatalKG`

2. **Turtle é uma sintaxe legível para escrever RDF:**
   - Usa prefixos (@prefix) para encurtar URIs
   - Termina sentenças com ponto (.)
   - É case-sensitive!

3. **Cada "coisa" tem uma URI:**
   - `ex:Clarimar` = `http://example.org/Clarimar`
   - URIs são globalmente únicos

4. **RDFLib valida e processa RDF em Python:**
   - Carrega arquivos Turtle
   - Permite queries
   - Serializa em diferentes formatos

### 🎯 Arquivos criados hoje:

- ✅ `01_first_rdf_triple.ttl` - Meu primeiro arquivo RDF!
  - 12 triplas sobre mim e o projeto
  - Validado com RDFLib
  - Funciona perfeitamente! 🎉

- ✅ `validate_first_rdf.py` - Script de validação
  - Carrega o .ttl
  - Mostra as triplas de forma legível
  - Confirma que o RDF está correto

### 📊 Estatísticas:

- **Triplas criadas:** 12
- **Namespaces usados:** 4 (ex, rdf, rdfs, xsd)
- **Tempo gasto:** ~2 horas
- **Sensação:** 🎉 Empolgante!

### 🎯 Próximos passos (Semana 2):

- [ ] Aprender SPARQL (query language)
- [ ] Criar ontologia mínima com classes
- [ ] Usar Protégé (editor visual)
- [ ] Instalar Apache Jena Fuseki
- [ ] Baixar dados SIM e IBGE

### 📝 Notas importantes que descobri:

- URIs não precisam ser "resolvíveis" (não precisam abrir no navegador)
- Turtle é case-sensitive: `ex:Person` ≠ `ex:person`
- Todo RDF válido pode ser convertido para outros formatos (N-Triples, JSON-LD)
- RDFLib é MUITO fácil de usar!

### 🔗 Recursos que usei:

- W3C Turtle Spec: https://www.w3.org/TR/turtle/
- RDFLib Docs: https://rdflib.readthedocs.io/
- Exemplos do guia do Guilherme

### 💭 Reflexões:

RDF parecia complicado no início, mas depois que você entende
o conceito de triplas (sujeito-predicado-objeto), tudo faz sentido!

É como construir um grafo com sentenças simples.

Estou animado para aprender SPARQL na próxima semana! 🚀

---

## 📅 Week 2 - Day 6-10 (Coming soon...)

[A ser preenchido]

---

**Tempo total Week 1:** ~2 horas  
**Status:** ✅ Concluída com sucesso!
