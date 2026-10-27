# Disney Explode para Linux

Edição reduzida de terminal: CPU, memória, discos montados, temperaturas disponíveis em sysfs e exportação JSON. Não exige sudo.

```bash
chmod +x DisneyExplode-linux-x64
./DisneyExplode-linux-x64
./DisneyExplode-linux-x64 --output relatorio.json
./DisneyExplode-linux-x64 --json
```

Também é possível executar o código com Python 3.12+: `python3 linux/disney_explode.py`.

O binário é destinado a Linux x64 com glibc 2.35+ (Ubuntu 22.04 ou mais recente). A interface WPF, DirectX, drivers, overclock, otimizações do Windows e integrações RGB não estão disponíveis nesta edição. Temperaturas dependem dos sensores expostos pelo sistema; discos sem permissão de leitura são ignorados.
