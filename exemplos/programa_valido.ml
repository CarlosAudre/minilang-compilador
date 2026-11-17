// Programa válido com while e for
x = 10;
y = 2 * (x + 5);
while (x > 0) {
  print(x);
  x = x - 1;
}
soma = 0;
for (i = 0; i < 5; i = i + 1) {
  soma = soma + i;
}
if (soma > 20) {
  print(soma);
} else {
  print(0);
}