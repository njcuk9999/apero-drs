---
card_label: Add Product
card_icon: fa-solid fa-circle-question
---

# How to add a reduction product to the objects directory

1. Open `manual_trigger` yaml files for both HE and HA.
2. Edit `get: science out types:`.
3. Add the APERO product `name` you want linked.
4. Run:

```bash
manual_trigger
python manual_trigger.py {yaml_file} --only_aperoget
```

Apply consistently to online/offline yaml files to keep behavior aligned.
