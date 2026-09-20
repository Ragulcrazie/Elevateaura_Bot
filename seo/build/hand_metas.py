"""Hand-written replacements for the seven descriptions too long for search results.

Each keeps the primary keyword and the strongest reason to click, and drops the trailing
call to action, which the snippet never had room for anyway.
"""
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NEW = {
 "aura-business/healthcare-crm-software/index.html":
 "Healthcare CRM software for Indian medical businesses: hospitals, doctors and dealers in one database, with leads, follow-ups, service and AMC on the same record.",
 "aura-business/medical-equipment-inventory-software/index.html":
 "Medical equipment inventory software covering stock across warehouses and engineer vans, spare parts, batch and expiry, HSN, purchase orders and reorder alerts.",
 "aura-learn/learning-management-system/index.html":
 "A learning management system with a learner app and instructor dashboard: courses, video, quizzes, mock tests, certificates and live classes, for unlimited learners.",
 "auracare/elderly-home-care/index.html":
 "Nurse-led elderly home care in the Chengalpattu and South Chennai belt: medication, diabetes and BP monitoring, mobility, hygiene and bedridden care at home.",
 "auracare/post-hospitalization-home-care/index.html":
 "Post-hospitalisation home care by a registered nurse in Chengalpattu and South Chennai: wound and drain care, medication, vitals and mobility support after discharge.",
 "hims/hospital-inventory-management/index.html":
 "Hospital inventory management software for central stores: consumables and surgical items by batch and expiry, ward indents, GRN, reorder alerts and asset tracking.",
 "product-development/device-companion-app-development/index.html":
 "Device companion app development: a React Native app that pairs with your hardware over BLE or Wi-Fi, shows status, controls the device and triggers OTA updates.",
}


def main():
    for f, d in NEW.items():
        s = io.open(f, encoding="utf-8").read()
        m = re.search(r'<meta name="description" content="(.*?)"', s, re.S)
        if not m or m.group(1) == d:
            print("skip", f)
            continue
        s = s.replace('<meta name="description" content="%s"' % m.group(1),
                      '<meta name="description" content="%s"' % d, 1)
        io.open(f, "w", encoding="utf-8", newline="\n").write(s)
        print("%3d -> %3d  %s" % (len(m.group(1)), len(d), f))


if __name__ == "__main__":
    main()
