# Cobertura IBGE

## Dados disponíveis
- **População 2022:** 5,570 municípios (100%)
- **IDH-M 2010:** 23,562 registros → 5,565 municípios únicos (99.9%)

## Dados não obtidos
- **Renda per capita 2010:** API IBGE SIDRA retornou erro 500
  - Causa: tabela indisponível no servidor IBGE
  - Alternativa: IDH-M inclui componente de renda (proxy aceitável)

## Impacto no Paper
- IDH-M é indicador composto (renda + educação + saúde)
- Substitui renda per capita como indicador socioeconômico
- Amplamente usado em literatura epidemiológica brasileira
- Cobertura de 99.9% é excelente

## Nota metodológica
Para o Paper 1 (metodológico), IDH-M como indicador
socioeconômico é escolha defensável e amplamente aceita.
