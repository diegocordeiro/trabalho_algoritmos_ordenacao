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

TAMANHOS_OBRIGATORIOS = [50, 100, 500, 1000, 5000, 30000, 50000, 100000, 150000, 200000]


class ConfiguracaoBenchmarkForm(forms.Form):
    nome = forms.CharField(max_length=120, required=False)
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
        choices=[(str(t), f'{t:,}'.replace(',', '.')) for t in TAMANHOS_OBRIGATORIOS] + [('outro', 'Outro (especificar)')],
        initial=str(TAMANHOS_OBRIGATORIOS[0]),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )
    tamanho_personalizado = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite o tamanho desejado',
        })
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
    permitir_repetidos = forms.BooleanField(
        required=False,
        initial=False,
        label='Permitir números repetidos nos vetores',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def clean_condicoes(self):
        condicoes = self.cleaned_data['condicoes']
        if len(condicoes) < 1:
            raise forms.ValidationError('Selecione ao menos uma condição.')
        return condicoes

    def clean(self):
        cleaned_data = super().clean()
        tamanho = cleaned_data.get('tamanho')
        vetor_personalizado = cleaned_data.get('vetor_personalizado')
        tamanho_personalizado = cleaned_data.get('tamanho_personalizado')

        if vetor_personalizado and vetor_personalizado.strip():
            vetor_parsed = [int(x.strip()) for x in vetor_personalizado.split(',') if x.strip()]
            tem_repetidos = len(vetor_parsed) != len(set(vetor_parsed))
            cleaned_data['permitir_repetidos'] = tem_repetidos
            return cleaned_data

        if not tamanho:
            self.add_error('tamanho', 'Selecione um tamanho.')
        elif tamanho == 'outro':
            if not tamanho_personalizado:
                self.add_error('tamanho_personalizado', 'Informe o tamanho desejado.')
        return cleaned_data
