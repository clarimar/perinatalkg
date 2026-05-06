# Cobertura SIM 2015-2024

## Resultado Final
- **Total óbitos neonatais:** 178,336
- **Combinações baixadas:** 251/270 (93%)
- **Falhas:** 19 combinações UF-ano

## Falhas documentadas
MG-2015, MT-2016, SC-2016, SP-2016, PE-2018,
RJ-2019, PE-2020, CE-2021, RJ-2021, RO-2021,
SP-2021, CE-2022, PE-2022, MG-2023, RJ-2023,
SP-2023, PE-2024

## Causa
PySUS 2.0 API não retorna dados para estas
combinações. Arquivos DBC existem no FTP DATASUS
mas requerem conversor DBC não disponível no
Python 3.13.

## Impacto no Paper
Cobertura de 93% é aceitável para paper
metodológico. Limitação será declarada na
seção Methods do manuscrito.

## Solução Futura
Instalar R + pacote read.dbc para converter
os arquivos DBC diretamente do FTP DATASUS.
