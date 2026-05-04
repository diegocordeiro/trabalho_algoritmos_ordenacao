from django import forms

ALGORITMOS_DISPONIVEIS = [
    ('bublesort', 'Bublesort'),
    ('insertionsort', 'Insertionsort'),
    ('mergesort', 'MergeSort'),
    ('heap', 'HeapSort'),
    ('quicksort', 'QuickSort'),
]

CONDICOES_DISPONIVEIS = [
    ('crescente', 'Crescente'),
    ('decrescente', 'Decrescente'),
    ('aleatorio', 'Aleatorio'),
]

TAMANHOS_OBRIGATORIOS = [100, 500, 1000, 5000, 30000, 50000, 100000, 150000, 200000]


class ConfiguracaoBenchmarkForm(forms.Form):
    nome = forms.CharField(max_length=120, required=False, initial='Execucao Parte I')
    algoritmo = forms.ChoiceField(
        choices=ALGORITMOS_DISPONIVEIS,
        initial=ALGORITMOS_DISPONIVEIS[0][0],
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )
    condicoes = forms.MultipleChoiceField(
        choices=CONDICOES_DISPONIVEIS,
        initial=[CONDICOES_DISPONIVEIS[0][0]],
        widget=forms.CheckboxSelectMultiple,
    )
    tamanho = forms.ChoiceField(
        choices=[(str(t), f'{t:,}'.replace(',', '.')) for t in TAMANHOS_OBRIGATORIOS],
        initial=str(TAMANHOS_OBRIGATORIOS[0]),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )
    repeticoes = forms.IntegerField(
        min_value=3,
        initial=3,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg'})
    )
    vetor_personalizado = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'placeholder': 'Opcional: ex: 9,2,7,4,1',
                'class': 'form-control',
            }
        )
    )

    def clean_condicoes(self):
        condicoes = self.cleaned_data['condicoes']
        if len(condicoes) < 1:
            raise forms.ValidationError('Selecione ao menos uma condição.')
        return condicoes
