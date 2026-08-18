# Technický protokol: Lovec magnetických anomálií

**Autor:** František  
**Dátum merania:** 18. august 2026  
**Merací objekt:** obal slúchadiel Audio-Technica ATH-CKS50TW  
**Merací prístroj:** magnetometer telefónu iPhone 15

## Otázka

Ako sa mení veľkosť vektorovej odchýlky magnetického poľa od pozadia pri zväčšovaní medzery medzi prednou stranou obalu ATH-CKS50TW a hranou telefónu?

## Metóda

Telefón ležal vodorovne na označenom mieste. Obal bol otočený prednou stranou s magnetom k hornej hrane telefónu a posúval sa priamo od nej. Merania sa vykonali pri medzerách 0 cm, 5 cm, 10 cm a 20 cm. Každý bod bol zopakovaný trikrát. Pozadie sa zmeralo na začiatku a na konci experimentu.

Magnetometer sa nachádza približne 2 cm od hornej a 1,5 cm od pravej hrany telefónu. Nulová medzera preto neznamená nulovú vzdialenosť od senzora.

Pre každé opakovanie sa vypočítal priemerný vektor poľa. Referencia bola vytvorená ako priemer počiatočného a koncového vektora pozadia. Veľkosť anomálie bola určená vzťahom:

```text
ΔB = sqrt(ΔBx² + ΔBy² + ΔBz²)
