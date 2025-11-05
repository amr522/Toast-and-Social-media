# Missing Menu Item Images

**Last Updated:** November 4, 2025  
**Total Missing:** 83 items

The following menu items currently lack corresponding images in the `data/` directory. Images should be named using the slug format (e.g., `alfredo-linguine-or-penne.png` or `.jpg`).

## Dinner Items

- alfredo-linguine-or-penne
- baby-back-ribs
- baby-shrimp-scampi-and-garlic-bread
- blackened-cod
- bruschetta-variety
- cheese-ravioli
- chicken-francaise
- chicken-marsala
- chicken-parmesan-sandwich
- chicken-parmigiana
- chicken-piccata
- chicken-scampi
- clams-portofino
- classic-fettuccini-alfredo
- fettuccini-bolognese
- flatbread-variety
- fried-breaded-mozzarella
- gluten-free-garden-pasta
- house-lasagna
- meatballs-side
- mussels-red-or-white
- pink-vodka-linguine-or-penne
- pink-vodka-pasta
- pork-chop-marsala
- quattro-formaggi-ravioli
- sausage-parmesan
- sausage-tomato-sauce
- sauteed-broccoli
- sauteed-spinach
- shrimp-parmigiana
- sicilian-penne
- veal-capricciosa
- veal-marsala
- veal-parmesan

## Lunch Items

- avocado-fusion-delight
- burger-avocado-fusion
- cajun-chicken-lunch
- calamari-fra-diavolo-lunch
- cheese-ravioli-lunch
- chicken-avocado-fusion-sandwich
- chicken-caprese-sandwich
- chicken-francaise-lunch
- chicken-marsala-lunch
- chicken-parmesan-lunch
- chicken-piccata-lunch
- eggplant-parmigiana-lunch
- fettuccini-bolognese-lunch
- gluten-free-pasta-lunch
- grilled-shrimp-plate
- lasagna-lunch
- linguine-with-meatballs-lunch
- meatball-parmesan-sandwich
- philly-cheesesteak
- shrimp-parmesan-lunch
- shrimp-parmesan-sandwich
- sicilian-penne-lunch
- veal-parmesan-sandwich

## Sandwiches & Burgers

- black-and-blue-cajun-burger
- smoky-bbq-bacon-burger

## Happy Hour Items

- calamari-hh
- chicken-tenders-hh
- mussels-hh
- wings-hh

## Salads

- caesar-salad
- caprese-salad
- capricciosa-salad
- house-salad
- salad-addons
- salad-protein-addons

## Appetizers

- caprese
- chicken-wings
- fried-calamari
- fried-mozzarella
- fried-ravioli
- mozzarella-and-tomato-tower
- soup-of-the-day
- tuna-ceviche

## Flatbreads

- coastal-chicken-flatbread
- mediterranean-bliss-flatbread
- pesto-chicken-delight-flatbread
- pietros-fig-bacon-flatbread
- shrimp-sensation-flatbread
- tuscan-roasted-chicken-flatbread

---

## How to Add Images

1. **Capture or source** high-quality photos of the missing items
2. **Name the file** using the exact slug from the list above (e.g., `alfredo-linguine-or-penne.jpg`)
3. **Place the file** in the `data/` directory
4. **Run validation** to confirm parity:
   ```bash
   python3 -m src.tools.validate_assets
   ```
5. **Export and process** the new items:
   ```bash
   python3 -m src.menu.export_items
   python3 -m src.pipeline.run_once
   ```
6. **Commit and push** the updates to GitHub

## Tracking Progress

After adding images, this file will be automatically updated by running:
```bash
python3 -m src.tools.validate_assets --update-missing-list
```

The validation script also generates a `build/manifest.csv` that tracks the current state of all menu items.
