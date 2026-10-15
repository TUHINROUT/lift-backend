import io
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm


def generate_guidex_9page_pdf(proposal_data: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )
    styles = getSampleStyleSheet()

    header_sub = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#333333')
    )
    bold_txt = ParagraphStyle(
        'BoldTxt',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13
    )
    body_txt = ParagraphStyle(
        'BodyTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13
    )
    table_txt = ParagraphStyle(
        'TableTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11
    )
    table_bold = ParagraphStyle(
        'TableBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11
    )

    letter = proposal_data.get('page_2_letter', {})
    specs = proposal_data.get('page_3_and_4_technical_specifications', {})
    pricing = proposal_data.get('page_5_features_and_pricing', {}).get('price_schedule', {})
    brands = proposal_data.get('page_7_and_8_specifications_and_brands', {}).get('brands', [])

    def get_header():
        head_data = [
            [
                Paragraph("<b>GUIDEX ELEVATOR PVT. LTD.</b><br/><font size='8'>Bhubaneswar, Odisha<br/>Email: info@guidexelevator.com<br/>Website: www.guidexelevator.com</font>", header_sub),
                Paragraph("<font size='16' color='#C0292B'><b>▲ GUIDEX</b></font><br/><font size='7.5' color='#666'>The Safest Elevator</font>", ParagraphStyle('R', alignment=2, fontName='Helvetica-Bold'))
            ]
        ]
        t = Table(head_data, colWidths=[120 * mm, 60 * mm])
        t.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1.2, colors.HexColor('#222222')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        return t

    story = []

    # PAGE 1: COVER
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("<font color='#C0292B'><b>GUIDEX ELEVATOR PVT. LTD.</b></font>", ParagraphStyle('Cover1', alignment=1, fontSize=24, leading=28, fontName='Helvetica-Bold')))
    story.append(Paragraph("www.guidexelevator.com | info@guidexelevator.com", ParagraphStyle('Cover2', alignment=1, fontSize=11, leading=16, textColor=colors.HexColor('#555555'))))
    story.append(Spacer(1, 35 * mm))
    story.append(Paragraph("<b>The Safest Elevator of India</b>", ParagraphStyle('Cover3', alignment=1, fontSize=19, leading=24, fontName='Helvetica-Bold', textColor=colors.HexColor('#8B5A00'))))
    story.append(Paragraph("<b>As per IS17900 Standards</b>", ParagraphStyle('Cover4', alignment=1, fontSize=14, leading=18, textColor=colors.HexColor('#555555'))))
    story.append(Spacer(1, 55 * mm))
    story.append(Paragraph("<b>PROPOSAL FOR PASSENGER ELEVATOR</b>", ParagraphStyle('Cover5', alignment=1, fontSize=13, fontName='Helvetica-Bold')))
    story.append(Paragraph(f"Prepared for: <b>{letter.get('customer_name', '')}</b>", ParagraphStyle('Cover6', alignment=1, fontSize=11, leading=15)))
    story.append(Paragraph(f"Site: {letter.get('site_address', '')}", ParagraphStyle('Cover7', alignment=1, fontSize=10, textColor=colors.HexColor('#666666'))))
    story.append(PageBreak())

    # PAGE 2: LETTER
    story.append(get_header())
    story.append(Spacer(1, 4 * mm))
    ref_table = [
        [
            Paragraph(f"<b>Offer No :</b> {letter.get('offer_no', '')}", body_txt),
            Paragraph(f"<b>Date:</b> {letter.get('date', '')}", ParagraphStyle('DateR', alignment=2, fontName='Helvetica'))
        ]
    ]
    t_ref = Table(ref_table, colWidths=[100 * mm, 80 * mm])
    t_ref.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(t_ref)
    story.append(Spacer(1, 4 * mm))

    to_text = f"""<b>To,</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<b>{letter.get('customer_name', '')}</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;{letter.get('site_address', '')}<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;Contact: {letter.get('customer_contact', 'N/A')}<br/><br/>
    <b>Site Address:</b> {letter.get('site_address', '')}<br/><br/>
    <b>Sub:</b> {letter.get('subject', 'Supply, Installation, Testing and Commissioning of Elevator')}<br/><br/>
    Dear Sir,<br/><br/>
    This has reference to the discussion held between GUIDEX and you regarding the subject elevator.<br/><br/>
    As desired by you, we are submitting herewith our Proposal No. {letter.get('offer_no', '')} dated {letter.get('date', '')} in duplicate for your kind consideration and acceptance of the same.<br/><br/>
    While submitting the proposal, we would like to state that the same will remain valid for your kind acceptance for a period of {letter.get('validity_days', 30)} days from the date hereof.<br/><br/>
    Please note that no escalation in price is applicable. Our price shall remain firm for the period of 1 year from the date of agreement and the same will be subjected to revision thereafter as per the market rates ruling at the time.<br/><br/>
    Please sign and return one copy of our Proposal as a token of your acceptance along with the necessary advance payment to enable us to take up the job.<br/><br/>
    We sincerely hope that our quotation and other terms and conditions will be acceptable to you and you will favor us by placing your valued order at an early date.<br/><br/>
    Thanking and assuring you of our best services at all times.<br/><br/>
    Yours faithfully,<br/><br/>
    <b>GUIDEX ELEVATOR PVT. LTD.</b><br/>
    Office Contact: {letter.get('office_contact', '+91 9668654365')}
    """
    story.append(Paragraph(to_text, body_txt))
    story.append(PageBreak())

    # PAGE 3 & 4: TECHNICAL SPECIFICATIONS
    story.append(get_header())
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("<b>TECHNICAL SPECIFICATION</b>", bold_txt))
    story.append(Spacer(1, 2 * mm))

    spec_rows = [
        ["NO OF UNIT", specs.get('no_of_unit', '01 (One)')],
        ["TYPE", specs.get('type', '06 PASSENGERS')],
        ["LOAD", str(specs.get('load', '408 KG'))],
        ["SPEED", str(specs.get('speed', '1 MPS'))],
        ["CONTROL", specs.get('control', 'Microprocessor VVVF')],
        ["CAR TRAVEL", specs.get('car_travel', 'G + 3')],
        ["FLOOR RISE", str(specs.get('floor_rise', '12 Meters'))],
        ["NO OF OPENING", str(specs.get('no_of_opening', '4'))],
        ["NO OF STOPS", str(specs.get('no_of_stops', '4'))],
        ["OPERATION", specs.get('operation', 'Gearless / Machine Room Less')],
        ["CAR FINISH", specs.get('car_finish', 'SS Hairline')],
        ["CAR ENCLOSURE", specs.get('car_enclosure', '1.2MM')],
        ["CAR ENTRANCE DOOR", specs.get('car_entrance_door', 'SS Hairline')],
        ["CLEAR DOOR OPENING", specs.get('clear_door_opening', '700mm X 2000mm')],
        ["LIFT WELL", specs.get('lift_well', '1800mm X 1600mm')],
        ["CAR INSIDE", specs.get('car_inside', '1000mm X 1100mm')],
        ["OVER HEAD", specs.get('overhead', '4200mm')],
        ["PIT DEPTH", specs.get('pit_depth', '1500mm')],
        ["Cabin/ Car finish (All Side)", specs.get('cabin_finish', 'Hairline')],
        ["Door Finish", specs.get('door_finish', 'Side Opening Door with SS Hairline Finish')],
        ["Car Ceiling Finish", specs.get('car_ceiling_finish', 'SS Mirror (1.2MM Grade 304)')],
        ["Handrails", specs.get('handrails', 'SS Mirror Finish on rear Panel')],
        ["Ventilation", specs.get('ventilation', 'Cross Flow fan')],
        ["Flooring", specs.get('flooring', 'PVC / Wooden')],
        ["MACHINE UNIT", specs.get('machine_unit', '3 Phase PM Gearless Motor')],
        ["POWER SUPPLY", specs.get('power_supply', 'AC 440 V , 3 Phase 50 Hz')],
        ["Stabilizer", specs.get('stabilizer', 'Yes')]
    ]
    t_spec_data = [[Paragraph(f"<b>{r[0]}</b>", table_bold), Paragraph(str(r[1]), table_txt)] for r in spec_rows]
    t_specs = Table(t_spec_data, colWidths=[70 * mm, 110 * mm])
    t_specs.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FAFAFA')),
    ]))
    story.append(t_specs)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Customer's Sign: ___________________________", bold_txt))
    story.append(PageBreak())

    # PAGE 5: FEATURES & PRICING
    story.append(get_header())
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("<b>MAIN FEATURES & SAFETY SYSTEMS:</b>", bold_txt))
    story.append(Spacer(1, 2 * mm))

    feat_data = [
        [Paragraph("<b>MAIN FEATURES:</b>", table_bold), "", Paragraph("<b>SAFETY FEATURES:</b>", table_bold), ""],
        ["1", "Hassle Free Comprehensive maintenance (1 yr)", "1", "Overload protection"],
        ["2", "Fire rated landing doors - 60 Mins", "2", "Emergency Alarm"],
        ["3", "Door with mechanical lock", "3", "Infrared Door Protection Light Curtain"],
        ["4", "Anti Nuisance Car Call Protection", "4", "Emergency Stop Switch"],
        ["5", "Overspeed Protection for Lift Car (OSG)", "5", "Door Open & Close Button"],
        ["6", "Manual Rescue Operation", "6", "ARD System (Automatic Rescue Device)"]
    ]
    feat_table_rows = []
    for idx, r in enumerate(feat_data):
        if idx == 0:
            feat_table_rows.append([r[0], "", r[2], ""])
        else:
            feat_table_rows.append([
                Paragraph(f"<b>{r[0]}</b>", table_bold),
                Paragraph(r[1], table_txt),
                Paragraph(f"<b>{r[2]}</b>", table_bold),
                Paragraph(r[3], table_txt)
            ])
    t_feat = Table(feat_table_rows, colWidths=[8 * mm, 80 * mm, 8 * mm, 84 * mm])
    t_feat.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEEEEE')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("<b>PRICE SCHEDULE:</b>", bold_txt))
    story.append(Spacer(1, 2 * mm))
    total_val = float(pricing.get('total_price', 913700))
    price_table_data = [
        [Paragraph("<b>No of Lift</b>", table_bold), Paragraph("<b>Cost per each lift</b>", table_bold), Paragraph("<b>Total Price</b>", table_bold)],
        [Paragraph("1", table_txt), Paragraph(f"Rs. {total_val:,.2f}", table_txt), Paragraph(f"<b>Rs. {total_val:,.2f}</b>", table_bold)],
    ]
    t_price = Table(price_table_data, colWidths=[30 * mm, 75 * mm, 75 * mm])
    t_price.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_price)
    story.append(Spacer(1, 2 * mm))
    words = pricing.get('price_in_words', f"INR {total_val:,.2f}")
    t_words = Table([[Paragraph(f"<b>In Words:</b> {words}", bold_txt)]], colWidths=[180 * mm])
    t_words.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#777777')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA'))
    ]))
    story.append(t_words)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Customer's Sign: ___________________________", bold_txt))
    story.append(PageBreak())

    # PAGE 6: PAYMENT & TERMS
    story.append(get_header())
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("<b>Payment Terms</b>", bold_txt))
    story.append(Spacer(1, 2 * mm))
    p_terms = """
    &nbsp;&nbsp;&nbsp;&nbsp;<b>&gt; 20 %</b> On confirmation of Order.<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<b>&gt; 70 %</b> On intimation that material manufacturing.<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<i>(Material will deliver by 4 weeks from receipt of this payment)</i><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<b>&gt; 10 %</b> Before handing over or installation of lift.
    """
    story.append(Paragraph(p_terms, body_txt))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("<b>TERMS & CONDITIONS</b>", ParagraphStyle('TC', alignment=1, fontName='Helvetica-Bold', fontSize=11)))
    story.append(Spacer(1, 2 * mm))
    tc_body = f"""
    <b>Quotation Validity:</b><br/>
    ● This quotation is valid for {letter.get('validity_days', 30)} days from the date of issuance. After this period, the terms, prices, and specifications may be subject to revision.<br/><br/>
    <b>Scope of Work:</b><br/>
    <b>Customer Scope:</b><br/>
    ❖ <b>Complete Shaft Construction:</b> Civil works or fabrication required for the full lift shaft ({specs.get('lift_well', '1800 x 1600 mm')}).<br/>
    ❖ <b>Scaffolding of Shaft:</b> Provision and arrangement of scaffolding inside the shaft, as required for installation.<br/>
    ❖ <b>Electrical Wiring of Shaft and Earthing:</b> Completion of electrical wiring from the main panel to the lift machine point, with proper earthing as per safety standards.<br/><br/>
    <b>Company Scope:</b><br/>
    ● Complete Supply, Installation, Testing, and Commissioning of the Lift System as per specifications outlined in this quotation.
    """
    story.append(Paragraph(tc_body, body_txt))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Customer's Sign: ___________________________", bold_txt))
    story.append(PageBreak())

    # PAGE 7: DELIVERY & WARRANTY
    story.append(get_header())
    story.append(Spacer(1, 3 * mm))
    page7_text = """
    ● The quoted price includes the supply, installation, testing, and commissioning of the elevator system. Any additional requirements or modifications not mentioned in this quotation will be subject to additional charges.<br/><br/>
    <b>Delivery and Installation Timeline:</b><br/>
    ● The estimated total time for delivery, installation, and commissioning of the goods elevator is 3 months from the date of order confirmation and receipt of all required documentation.<br/>
    ● GUIDEX will notify the customer promptly if there are any delays due to unforeseen circumstances or force majeure events.<br/><br/>
    <b>Warranty:</b><br/>
    ● <b>GUIDEX provides a warranty for the elevator system for a period of 12 months from the date of successful installation and commissioning.</b><br/>
    ● This warranty covers the repair or replacement of any faulty or defective parts due to manufacturing or material defects.<br/><br/>
    <b>Installation and Site Conditions:</b><br/>
    ● The customer is responsible for ensuring that the installation site is fully prepared and meets the necessary conditions for installation, such as proper structural support, electrical connections, and accessibility.<br/><br/>
    <b>Maintenance:</b><br/>
    ● Post-installation maintenance services can be provided by GUIDEX on a separate service contract basis. Please contact GUIDEX for details regarding maintenance packages after the warranty period.<br/><br/>
    <b>Cancellation or Modification:</b><br/>
    ● Any cancellation or modification to the order after confirmation will incur a cancellation fee of 10% of the total contract value.
    """
    story.append(Paragraph(page7_text, body_txt))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Customer's Sign: ___________________________", bold_txt))
    story.append(PageBreak())

    # PAGE 8: LIABILITY & BRANDS
    story.append(get_header())
    story.append(Spacer(1, 3 * mm))
    page8_text = """
    <b>Liability:</b><br/>
    ● GUIDEX will not be held liable for any indirect, incidental, or consequential damages arising from delays, defects, or malfunctioning of the elevator system.<br/>
    ● GUIDEX's total liability under this agreement is limited to the repair or replacement of defective parts within the warranty period.<br/><br/>
    <b>Dispute Resolution:</b><br/>
    ● Any disputes or disagreements arising from this agreement shall first be resolved through amicable negotiations between the parties.<br/><br/>
    <b>Acceptance:</b><br/>
    ● By signing this agreement, the customer acknowledges acceptance of the terms and conditions outlined in this quotation.
    """
    story.append(Paragraph(page8_text, body_txt))
    story.append(Spacer(1, 3 * mm))

    brand_table_rows = [[Paragraph("<b>Parts</b>", table_bold), Paragraph("<b>Grade / Brand</b>", table_bold)]]
    for b in brands:
        brand_table_rows.append([Paragraph(b.get('parts', ''), table_txt), Paragraph(b.get('grade_brand', ''), table_txt)])
    t_brand = Table(brand_table_rows, colWidths=[65 * mm, 115 * mm])
    t_brand.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEEEEE')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_brand)
    story.append(Spacer(1, 4 * mm))
    sign_table = [
        [Paragraph("Customer's Sign: ___________________________", bold_txt), Paragraph("Guidex Employee Sign with Date", bold_txt)],
        [Paragraph("Date: ___________________________", body_txt), ""]
    ]
    t_sign = Table(sign_table, colWidths=[100 * mm, 80 * mm])
    story.append(t_sign)
    story.append(PageBreak())

    # PAGE 9: MAINTENANCE CONTRACT
    story.append(get_header())
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("<b>Maintenance Contract</b>", bold_txt))
    story.append(Spacer(1, 2 * mm))

    amc_table_data = [
        [Paragraph("<b>Year</b>", table_bold), Paragraph("<b>AMC/CMC</b>", table_bold), Paragraph("<b>Price</b>", table_bold), Paragraph("<b>No of Service/Year</b>", table_bold), Paragraph("<b>Work Details</b>", table_bold)],
        [Paragraph("1st Year, 2nd Year", table_txt), Paragraph("CMC , AMC", table_txt), Paragraph("Free", table_txt), Paragraph("8 Service / Year", table_txt), Paragraph("Safety Check , Maintenance , Cleaning", table_txt)]
    ]
    t_amc = Table(amc_table_data, colWidths=[28 * mm, 25 * mm, 18 * mm, 35 * mm, 74 * mm])
    t_amc.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#666666')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEEEEE')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_amc)
    story.append(Spacer(1, 4 * mm))

    amc_clauses = """
    • The contractor shall provide eight (8) preventive maintenance services per annum. Each service shall include a comprehensive safety inspection, mechanical and electrical maintenance, lubrication, adjustment, and cleaning of all lift components to ensure safe and reliable operation.<br/><br/>
    • In the event of a mantrap (entrapment of passengers inside the lift car), the contractor shall provide immediate emergency response, and rescue operations shall be carried out on a priority basis in accordance with statutory safety procedures.<br/><br/>
    • During the Warranty / Comprehensive Maintenance Contract (CMC) period, the contractor shall be responsible for the repair or replacement of all lift components, excluding consumable items such as indicator bulbs, cabin fans, and batteries.<br/><br/>
    • The contractor shall ensure breakdown attendance within one (1) working day from the time of complaint registration.<br/><br/>
    • All maintenance and repair activities shall be performed by qualified and authorized service engineers, in compliance with applicable safety standards, manufacturer guidelines, and statutory regulations.
    """
    story.append(Paragraph(amc_clauses, body_txt))
    story.append(Spacer(1, 6 * mm))

    end_sign = [
        [Paragraph("Customer's Sign: ___________________________", bold_txt), Paragraph("Guidex Employee Sign with Date", bold_txt)],
        [Paragraph("Date: ___________________________", body_txt), ""]
    ]
    t_endsign = Table(end_sign, colWidths=[100 * mm, 80 * mm])
    story.append(t_endsign)

    doc.build(story)
    return buffer.getvalue()