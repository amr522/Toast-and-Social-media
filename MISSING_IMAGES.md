# Missing Menu Item Images

**Last Updated:** November 5, 2025  
**Total Missing (unique names):** 75

The following dishes currently lack corresponding images in the `data/` directory. This list is de‑duplicated by dish name across dinner and lunch — if a dish appears on both menus, one photo covers both. Images should be named using the canonical slug shown (e.g., `caesar-salad.jpg`), `.png` is also accepted.

## Shared (Dinner + Lunch)

- Avocado Fusion Delight (slug: `avocado-fusion-delight`)
- Caesar Salad (slug: `caesar-salad`)
- Capricciosa Salad (slug: `capricciosa-salad`)
- Cheese Ravioli (slug: `cheese-ravioli`)
- Chicken Marsala (slug: `chicken-marsala`)
- Chicken Piccata (slug: `chicken-piccata`)
- Clams Portofino (slug: `clams-portofino`)
- Fettuccini Bolognese (slug: `fettuccini-bolognese`)
- Fried Calamari (slug: `fried-calamari`)
- House Salad (slug: `house-salad`)
- Sicilian Penne (slug: `sicilian-penne`)
- Soup of the Day (slug: `soup-of-the-day`)
- Tuna Ceviche (slug: `tuna-ceviche`)

## Dinner‑Only

- Baby Back Ribs (slug: `baby-back-ribs`)
- Caprese (slug: `caprese-salad`)
- Chicken Parmigiana (slug: `chicken-parmigiana`)
- Chicken Scampi (slug: `chicken-scampi`)
- Fettuccini Alfredo (slug: `classic-fettuccini-alfredo`)
- Fried Breaded Fresh Mozzarella (slug: `fried-breaded-mozzarella`)
- Gamberi Ala Griglia (slug: `grilled-shrimp-plate`)
- Gluten‑Free Penne Pasta (slug: `gluten-free-garden-pasta`)
- Meat Lasagna (slug: `house-lasagna`)
- Meatballs with Tomato Sauce (slug: `meatballs-side`)
- Penne Pink Vodka (slug: `pink-vodka-pasta`)
- Quattro Formaggi Ravioli (slug: `quattro-formaggi-ravioli`)
- Ribeye Pork Chop Frostiera (slug: `pork-chop-marsala`)
- Salad Protein Add‑Ons (slug: `salad-protein-addons`)
- Sausage with Tomato Sauce (slug: `sausage-tomato-sauce`)
- Sautéed Broccoli (slug: `sauteed-broccoli`)
- Sautéed Spinach (slug: `sauteed-spinach`)
- Shrimp Parmigiana (slug: `shrimp-parmigiana`)
- Veal Capricciosa (slug: `veal-capricciosa`)
- Veal Marsala (slug: `veal-marsala`)
- Veal Parmigiana (slug: `veal-parmesan`)

## Lunch‑Only

- Alfredo (Linguine or Penne) (slug: `alfredo-linguine-or-penne`)
- Avocado Fusion Burger (slug: `burger-avocado-fusion`)
- Baby Shrimp Scampi and Garlic Bread (slug: `baby-shrimp-scampi-and-garlic-bread`)
- BBQ Bacon Burger (slug: `smoky-bbq-bacon-burger`)
- Bruschetta Trio (slug: `bruschetta-variety`)
- Cajun Chicken (slug: `cajun-chicken-lunch`)
- Calamari (Happy Hour) (slug: `calamari-hh`)
- Calamari Fra Diavolo (slug: `calamari-fra-diavolo-lunch`)
- Caprese Salad (slug: `caprese`)
- Chicken Avocado Fusion (slug: `chicken-avocado-fusion-sandwich`)
- Chicken Caprese (slug: `chicken-caprese-sandwich`)
- Chicken Parmesan (slug: `chicken-parmesan-lunch`)
- Chicken Parmesan Sandwich (slug: `chicken-parmesan-sandwich`)
- Chicken Tenders with Honey Mustard (slug: `chicken-tenders-hh`)
- Chicken Wings (slug: `chicken-wings`)
- Coastal Chicken Flatbread (slug: `coastal-chicken-flatbread`)
- Flatbread Variety (slug: `flatbread-variety`)
- Fried Fresh Mozzarella (slug: `fried-mozzarella`)
- Fried Ravioli (slug: `fried-ravioli`)
- Gluten‑Free Pasta (slug: `gluten-free-pasta-lunch`)
- Lasagna (slug: `lasagna-lunch`)
- Margherita (slug: `margherita-flatbread`)
- Meatball Parmesan (slug: `meatball-parmesan-sandwich`)
- Mediterranean Flatbread (slug: `mediterranean-bliss-flatbread`)
- Mozzarella and Tomato Tower (slug: `mozzarella-and-tomato-tower`)
- Mushroom Swiss Burger (slug: `black-and-blue-cajun-burger`)
- Mussels (Happy Hour) (slug: `mussels-hh`)
- Pesto Chicken Delight Flatbread (slug: `pesto-chicken-delight-flatbread`)
- Philly Cheesesteak (slug: `philly-cheesesteak`)
- Pietro's Fig & Bacon Flatbread (slug: `pietros-fig-bacon-flatbread`)
- Pink Vodka (Linguine or Penne) (slug: `pink-vodka-linguine-or-penne`)
- Shrimp Parmesan (slug: `shrimp-parmesan-lunch`)
- Shrimp Parmesan Sandwich (slug: `shrimp-parmesan-sandwich`)
- Sicilian Penne (Lunch) (slug: `sicilian-penne-lunch`)
- Linguine with Meatballs (Lunch) (slug: `linguine-with-meatballs-lunch`)
- Chicken Francaise (Lunch) (slug: `chicken-francaise-lunch`)
- Chicken Piccata (Lunch) (slug: `chicken-piccata-lunch`)
- Chicken Marsala (Lunch) (slug: `chicken-marsala-lunch`)
- Eggplant Parmigiana (Lunch) (slug: `eggplant-parmigiana-lunch`)

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

After adding images, rebuild the manifest and update this list with:
```bash
python3 -m src.tools.validate_assets --verbose
```

The validation script also generates a `build/manifest.csv` that tracks the current state of all menu items.
