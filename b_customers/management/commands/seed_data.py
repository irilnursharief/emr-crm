from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random
from b_customers.models import Customer
from c_devices.models import Device
from d_repairs.models import Repair
from datetime import datetime

User = get_user_model()
fake = Faker("en_PH")  # Philippine locale for realistic data


class Command(BaseCommand):
    help = "Seed the database with mock data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--customers",
            type=int,
            default=20,
            help="Number of customers to create (default: 20)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        num_customers = options["customers"]
        clear = options["clear"]

        if clear:
            self.stdout.write("🗑️  Clearing existing data...")

            from d_repairs.models import RepairNote
            from e_quotations.models import Quotation, QuotationItem
            from f_payments.models import Payment

            # Delete in correct dependency order
            RepairNote.objects.all().delete()
            Payment.objects.all().delete()
            QuotationItem.objects.all().delete()
            Quotation.objects.all().delete()
            Repair.objects.all().delete()
            Device.objects.all().delete()
            Customer.objects.all().delete()

            self.stdout.write(self.style.WARNING("Existing data cleared."))

        import datetime

        current_date = datetime.date.today().strftime("%m%d")
        repair_counter = 1

        # Get a system user to assign as created_by
        admin_user = User.objects.filter(role__in=["admin"]).first()

        if not admin_user:
            self.stdout.write(
                self.style.ERROR(
                    "No admin user found. Create one first via createsuperuser."
                )
            )
            return

        assignable_users = list(User.objects.filter(role__in=["technician", "admin"]))

        if not assignable_users:
            self.stdout.write(
                self.style.WARNING("No technicians found. Repairs will be unassigned.")
            )

        self.stdout.write(f"🌱 Seeding {num_customers} customers...")

        device_types = [
            Device.DeviceType.LAPTOP,
            Device.DeviceType.PHONE,
            Device.DeviceType.TABLET,
            Device.DeviceType.CONSOLE,
            Device.DeviceType.OTHER,
        ]

        brands = {
            "laptop": ["ASUS", "Lenovo", "HP", "Dell", "Acer", "Apple", "MSI"],
            "phone": ["Samsung", "Apple", "Xiaomi", "OPPO", "vivo", "realme"],
            "tablet": ["Apple", "Samsung", "Lenovo", "Huawei"],
            "console": ["Sony", "Microsoft", "Nintendo"],
            "other": ["Generic", "Custom Build"],
        }

        models_map = {
            "ASUS": ["VivoBook 15", "ROG Zephyrus G14", "TUF Gaming F15", "ZenBook 14"],
            "Lenovo": ["ThinkPad X1", "IdeaPad 5", "Legion 5", "Yoga 7i"],
            "HP": ["Pavilion 15", "Spectre x360", "Envy 13", "Omen 16"],
            "Dell": ["XPS 13", "Inspiron 15", "Latitude 7420", "G15 Gaming"],
            "Acer": ["Swift 3", "Aspire 5", "Predator Helios 300", "Nitro 5"],
            "Apple": [
                "MacBook Pro M3",
                "MacBook Air M2",
                "iPhone 15 Pro",
                "iPad Pro M4",
            ],
            "MSI": ["GF63 Thin", "Raider GE76", "Sword 15"],
            "Samsung": ["Galaxy S24", "Galaxy A54", "Galaxy Tab S9"],
            "Xiaomi": ["Redmi Note 13", "Mi 13T Pro", "POCO X5"],
            "OPPO": ["Reno 11", "Find X7", "A98"],
            "vivo": ["V30 Pro", "X90", "Y36"],
            "realme": ["GT 5 Pro", "11 Pro", "Narzo 60"],
            "Sony": ["PlayStation 5", "PlayStation 4 Pro"],
            "Microsoft": ["Xbox Series X", "Xbox Series S"],
            "Nintendo": ["Switch OLED", "Switch Lite"],
            "Huawei": ["MatePad Pro", "MediaPad M6"],
            "Generic": ["Custom PC", "Build PC"],
            "Custom Build": ["Desktop PC", "Mini ITX Build"],
        }

        issue_categories = [
            "No Power",
            "Screen Damage",
            "Battery Issue",
            "Charging Problem",
            "Keyboard/Touchpad Issue",
            "Overheating",
            "Software Issue",
            "Water Damage",
            "Speaker/Audio Issue",
            "Camera Issue",
            "Motherboard Failure",
            "Hard Drive Issue",
        ]

        peripherals_options = [
            "Charger",
            "Charger, Mouse",
            "Charger, Bag",
            "Mouse, Keyboard",
            "Charger, Headset",
            "",
            "",
            "",
        ]

        # Create customers
        customers_created = 0
        devices_created = 0
        repairs_created = 0
        quotations_created = 0
        items_created = 0
        payments_created = 0

        for i in range(num_customers):
            customer = Customer.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                contact_number=fake.numerify("09#########"),
                email=fake.email() if random.random() > 0.2 else "",
                address=fake.address() if random.random() > 0.3 else "",
                created_by=admin_user,
            )
            customers_created += 1

            # Each customer has 1-3 devices
            num_devices = random.randint(1, 3)
            for _ in range(num_devices):
                device_type = random.choice(device_types)
                type_key = device_type.value
                brand_list = brands.get(type_key, ["Generic"])
                brand = random.choice(brand_list)
                model_list = models_map.get(brand, ["Model X"])
                model = random.choice(model_list)

                device = Device.objects.create(
                    customer=customer,
                    type=device_type,
                    brand=brand,
                    model=model,
                    serial_number=fake.unique.bothify(text="??####??####").upper(),
                    peripherals=random.choice(peripherals_options),
                    created_by=admin_user,
                )
                devices_created += 1

                # Each device has 0-2 repairs
                num_repairs = random.randint(0, 2)
                for _ in range(num_repairs):
                    issue_cat = random.choice(issue_categories)

                    # Generate the human-readable ID
                    generated_repair_id = f"ERM-{current_date}-{repair_counter:03d}"

                    repair = Repair.objects.create(
                        repair_id=generated_repair_id,
                        device=device,
                        issue_category=issue_cat,
                        issue_description=fake.paragraph(nb_sentences=2),
                        vmi=random.choice(
                            [
                                "Minor scratches on the body.",
                                "Cracked screen, unit powers on.",
                                "No visible physical damage.",
                                "Dent on the corner, screen intact.",
                                "Water damage indicator triggered.",
                                "Heavy scratches on back panel.",
                            ]
                        ),
                        mi=random.choice(
                            [
                                "Burnt component detected on motherboard.",
                                "Battery health at 45%, swollen.",
                                "Screen backlight failure confirmed.",
                                "",
                                "",
                            ]
                        ),
                        diagnosis=random.choice(
                            [
                                "Faulty charging IC.",
                                "Defective battery.",
                                "Damaged LCD panel.",
                                "Corrupted OS partition.",
                                "",
                                "",
                            ]
                        ),
                        recommendation=random.choice(
                            [
                                "Replace charging IC.",
                                "Battery replacement required.",
                                "LCD panel replacement.",
                                "OS reinstallation.",
                                "",
                                "",
                            ]
                        ),
                        status=random.choice(Repair.Status.values),
                        assigned_to=(
                            random.choice(assignable_users)
                            if assignable_users and random.random() > 0.15
                            else None
                        ),
                        created_by=admin_user,
                    )
                    repair_counter += 1
                    repairs_created += 1

                    # --- Create Quotation (70% chance) ---
                    if random.random() > 0.3:
                        from e_quotations.models import Quotation, QuotationItem
                        from f_payments.models import Payment
                        from decimal import Decimal

                        quotation_status = random.choice(
                            [
                                Quotation.Status.DRAFT,
                                Quotation.Status.SENT,
                                Quotation.Status.APPROVED,
                                Quotation.Status.APPROVED,
                                Quotation.Status.APPROVED,
                            ]
                        )

                        discount = Decimal(
                            random.choice(
                                [
                                    "0.00",
                                    "0.00",
                                    "0.00",
                                    "100.00",
                                    "200.00",
                                    "500.00",
                                ]
                            )
                        )

                        quotation = Quotation.objects.create(
                            repair=repair,
                            status=quotation_status,
                            discount_amount=discount,
                            created_by=admin_user,
                        )
                        quotations_created += 1

                        # --- Create 1-4 Line Items ---
                        num_items = random.randint(1, 4)
                        for _ in range(num_items):
                            item_type = random.choice(QuotationItem.ItemType.values)
                            qty = random.randint(1, 3)
                            price = Decimal(
                                str(
                                    random.choice(
                                        [
                                            150,
                                            250,
                                            350,
                                            500,
                                            750,
                                            1000,
                                            1500,
                                            2000,
                                            2500,
                                            3000,
                                            3500,
                                            5000,
                                            7500,
                                        ]
                                    )
                                )
                            )

                            QuotationItem.objects.create(
                                quotation=quotation,
                                item_type=item_type,
                                description=random.choice(
                                    [
                                        "LCD Screen Replacement",
                                        "Battery Replacement",
                                        "Charging Port Repair",
                                        "Keyboard Replacement",
                                        "Motherboard Repair",
                                        "Thermal Paste Application",
                                        "OS Reinstallation",
                                        "Data Recovery",
                                        "Screen Protector Installation",
                                        "Deep Cleaning Service",
                                        "Fan Replacement",
                                        "Power IC Replacement",
                                        "Diagnostic Fee",
                                        "Labor Fee",
                                        "Rush Service Fee",
                                    ]
                                ),
                                quantity=qty,
                                unit_price=price,
                                warranty_days=random.choice(
                                    [
                                        None,
                                        None,
                                        7,
                                        15,
                                        30,
                                        60,
                                        90,
                                    ]
                                ),
                            )
                            items_created += 1

                        # --- Create Payments (only for Approved quotations) ---
                        if quotation_status == Quotation.Status.APPROVED:
                            total = quotation.total
                            remaining = total

                            # 60% chance of full payment, 40% partial
                            if random.random() > 0.4:
                                # Full payment
                                Payment.objects.create(
                                    repair=repair,
                                    amount=total,
                                    payment_type=Payment.PaymentType.FULL_SETTLEMENT,
                                    mode_of_payment=random.choice(
                                        Payment.PaymentMode.values
                                    ),
                                    reference_number=(
                                        fake.bothify(text="REF-####-????-####").upper()
                                        if random.random() > 0.5
                                        else ""
                                    ),
                                    created_by=admin_user,
                                )
                                payments_created += 1
                            else:
                                # Partial payments (1-3 payments)
                                num_payments = random.randint(1, 3)
                                for p in range(num_payments):
                                    if remaining <= 0:
                                        break

                                    if p == num_payments - 1:
                                        amount = remaining
                                        ptype = Payment.PaymentType.FULL_SETTLEMENT
                                    else:
                                        upper_bound = max(
                                            int(remaining * Decimal("0.6")), 100
                                        )
                                        lower_bound = min(100, int(remaining))

                                        amount = Decimal(
                                            str(
                                                random.randint(lower_bound, upper_bound)
                                            )
                                        )
                                        ptype = random.choice(
                                            [
                                                Payment.PaymentType.DOWN_PAYMENT,
                                                Payment.PaymentType.PARTIAL,
                                            ]
                                        )

                                    Payment.objects.create(
                                        repair=repair,
                                        amount=amount,
                                        payment_type=ptype,
                                        mode_of_payment=random.choice(
                                            Payment.PaymentMode.values
                                        ),
                                        reference_number=(
                                            fake.bothify(
                                                text="REF-####-????-####"
                                            ).upper()
                                            if random.random() > 0.5
                                            else ""
                                        ),
                                        created_by=admin_user,
                                    )
                                    payments_created += 1
                                    remaining -= amount

        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n✅ Seeding complete!"))
        self.stdout.write(f"   👤 Customers created:  {customers_created}")
        self.stdout.write(f"   📱 Devices created:    {devices_created}")
        self.stdout.write(f"   🔧 Repairs created:    {repairs_created}")
        self.stdout.write(f"   📋 Quotations created: {quotations_created}")
        self.stdout.write(f"   📦 Line items created: {items_created}")
        self.stdout.write(f"   💰 Payments created:   {payments_created}")
