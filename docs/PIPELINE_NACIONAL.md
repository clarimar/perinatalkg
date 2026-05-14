# PerinatalKG - Pipeline Nacional

## Escala Demonstrada (Goias 2015-2024)
- Nascimentos: 934,806
- Triplas RDF: 13,334,553
- Conversao: 210s (4,443 nasc/s)
- Carga Fuseki: 125s

## Benchmark SPARQL (13M triplas)
- COUNT preterm: 0.12s -> 101,287 (10.8%)
- COUNT LBW: 0.11s -> 83,660 (8.9%)
- COUNT extreme heat: 3.37s -> 387,012 (41.4%)
- AVG birthWeight: 0.46s -> 3,141g

## Projecao Brasil Completo
- 27M nascimentos -> 406M triplas
- Tempo sequencial: ~100 min
- Tempo paralelo (27 estados): ~4 min
- RAM Fuseki necessaria: ~32GB

## Para o Paper
The pipeline processes 4,400 births/s.
SPARQL queries over 13.3M triples: 0.1-7.6s.
