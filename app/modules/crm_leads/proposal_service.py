from datetime import datetime
from typing import Dict, Any

def render_guidex_proposal_html(data: Dict[str, Any]) -> str:
    letter = data.get("page_2_letter", {})
    specs = data.get("page_3_and_4_technical_specifications", {})
    pricing = data.get("page_5_features_and_pricing", {}).get("price_schedule", {})
    brands = data.get("page_7_and_8_specifications_and_brands", {}).get("brands", [])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>Proposal - {letter.get('offer_no')}</title>
      <style>
        @page {{
          size: A4 portrait;
          margin: 15mm 15mm 15mm 15mm;
        }}
        body {{
          font-family: Arial, Helvetica, sans-serif;
          color: #222;
          font-size: 11pt;
          line-height: 1.4;
          margin: 0;
          padding: 0;
        }}
        .page-break {{
          page-break-after: always;
          height: 0;
          display: block;
        }}
        .header {{
          border-bottom: 2px solid #333;
          padding-bottom: 10px;
          margin-bottom: 25px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }}
        .company-name {{
          color: #C0292B;
          font-size: 16pt;
          font-weight: bold;
          text-transform: uppercase;
        }}
        .company-sub {{
          font-size: 9pt;
          color: #444;
        }}
        .logo-box {{
          text-align: right;
          font-size: 16pt;
          font-weight: bold;
          color: #111;
        }}
        table.spec-table, table.data-table {{
          width: 100%;
          border-collapse: collapse;
          margin: 15px 0;
        }}
        table.spec-table th, table.spec-table td, table.data-table th, table.data-table td {{
          border: 1px solid #444;
          padding: 6px 10px;
          font-size: 10pt;
        }}
        table.spec-table th, table.data-table th {{
          background-color: #f2f2f2;
          text-align: left;
        }}
        .sign-row {{
          margin-top: 60px;
          display: flex;
          justify-content: space-between;
        }}
        .sign-line {{
          border-top: 1px dotted #333;
          width: 220px;
          text-align: center;
          padding-top: 5px;
          font-size: 10pt;
        }}
      </style>
    </head>
    <body>

      <!-- PAGE 1: COVER -->
      <div style="text-align: center; padding-top: 120px;">
        <h1 style="color: #C0292B; font-size: 26pt; margin-bottom: 5px;">GUIDEX ELEVATOR PVT. LTD.</h1>
        <p style="font-size: 11pt; color: #555;">www.guidexelevator.com | info@guidexelevator.com</p>
        <div style="margin: 90px 0;">
          <h2 style="font-size: 20pt; color: #222;">The Safest Elevator of India</h2>
          <h3 style="font-size: 14pt; color: #666; font-weight: normal;">As per IS 17900 Standards</h3>
        </div>
        <p style="font-size: 12pt; margin-top: 150px; font-weight: bold;">PASSENGER ELEVATOR PROPOSAL</p>
        <p style="font-size: 11pt; color: #444;">Prepared for: {letter.get('customer_name')}</p>
      </div>
      <div class="page-break"></div>

      <!-- PAGE 2: OFFER LETTER -->
      <div class="header">
        <div>
          <div class="company-name">GUIDEX ELEVATOR PVT. LTD.</div>
          <div class="company-sub">Bhubaneswar, Odisha | info@guidexelevator.com</div>
        </div>
        <div class="logo-box">▲ GUIDEX</div>
      </div>
      <p><strong>Offer No:</strong> {letter.get('offer_no')} <span style="float: right;"><strong>Date:</strong> {letter.get('date')}</span></p>
      <p style="margin-top: 15px;">To,<br/>
      <strong>{letter.get('customer_name')}</strong><br/>
      {letter.get('site_address')}<br/>
      <strong>Contact:</strong> {letter.get('customer_contact', 'N/A')}</p>

      <p style="margin-top: 15px;"><strong>Sub:</strong> {letter.get('subject')}</p>
      <p>Dear Sir,</p>
      <p>This has reference to the discussion held between GUIDEX and you regarding the subject elevator.</p>
      <p>As desired, we are submitting herewith our proposal for your kind consideration and acceptance. This proposal remains firm and valid for {letter.get('validity_days', 30)} days from the date hereof.</p>
      <p>Please sign and return one copy of this Proposal as a token of your acceptance along with the required advance payment to initiate engineering and fabrication.</p>
      
      <div class="sign-row" style="margin-top: 100px;">
        <div>Yours faithfully,<br/><br/><strong>For GUIDEX ELEVATOR PVT. LTD.</strong><br/>Authorized Signatory</div>
        <div class="sign-line" style="margin-top: 40px;">Customer Acceptance Signature</div>
      </div>
      <div class="page-break"></div>

      <!-- PAGE 3 & 4: TECHNICAL SPECIFICATIONS -->
      <div class="header">
        <div class="company-name">GUIDEX ELEVATOR PVT. LTD.</div>
        <div class="logo-box">▲ GUIDEX</div>
      </div>
      <h3 style="text-align: center; text-transform: uppercase;">Technical Specifications</h3>
      <table class="spec-table">
        <tr><td width="35%"><strong>Number of Units</strong></td><td>{specs.get('no_of_unit', '01 (One)')}</td></tr>
        <tr><td><strong>Type & Capacity</strong></td><td>{specs.get('type', '06 Passengers')} - {specs.get('load', '408 KG')}</td></tr>
        <tr><td><strong>Speed & Drive</strong></td><td>{specs.get('speed', '1.0 MPS')} / Microprocessor VVVF Closed Loop</td></tr>
        <tr><td><strong>Travel & Floor Rise</strong></td><td>{specs.get('car_travel')} ({specs.get('floor_rise')})</td></tr>
        <tr><td><strong>Number of Stops / Openings</strong></td><td>{specs.get('no_of_stops')} Stops / {specs.get('no_of_opening')} Openings</td></tr>
        <tr><td><strong>Operation Type</strong></td><td>{specs.get('operation')}</td></tr>
        <tr><td><strong>Available Shaft (W x D)</strong></td><td><strong>{specs.get('lift_well')}</strong></td></tr>
        <tr><td><strong>Internal Cabin (W x D)</strong></td><td>{specs.get('car_inside', '1100mm X 1000mm')}</td></tr>
        <tr><td><strong>Clear Door Opening</strong></td><td>{specs.get('clear_door_opening')}</td></tr>
        <tr><td><strong>Pit Depth / Overhead</strong></td><td>{specs.get('pit_depth')} / {specs.get('overhead')}</td></tr>
        <tr><td><strong>Cabin & Door Material</strong></td><td>SS Hairline 304 Grade (1.2 mm Enclosure)</td></tr>
        <tr><td><strong>Traction Machine</strong></td><td>{specs.get('machine_unit')}</td></tr>
        <tr><td><strong>Power Supply</strong></td><td>{specs.get('power_supply')}</td></tr>
      </table>
      <div class="sign-row">
        <div class="sign-line">GUIDEX Engineer</div>
        <div class="sign-line">Customer Signature</div>
      </div>
      <div class="page-break"></div>

      <!-- PAGE 5: FEATURES & PRICING -->
      <div class="header">
        <div class="company-name">GUIDEX ELEVATOR PVT. LTD.</div>
        <div class="logo-box">▲ GUIDEX</div>
      </div>
      <h3>Main & Safety Features</h3>
      <table class="data-table">
        <tr><th>Key Features</th><th>Safety Devices</th></tr>
        <tr>
          <td>
            • 1st Year Free Comprehensive Maintenance<br/>
            • Fire-Rated Landing Doors (60 mins)<br/>
            • Mechanical Interlocking Safety<br/>
            • Anti-Nuisance Car Call Protection<br/>
            • Manual Rescue Facility
          </td>
          <td>
            • Overload Audio-Visual Alarm<br/>
            • Full-Height Infrared Light Curtain Sensor<br/>
            • Emergency Stop Buttons in Car & Pit<br/>
            • Automatic Rescue Device (ARD Back-up)<br/>
            • Over-Speed Governor (OSG) Tripping
          </td>
        </tr>
      </table>

      <h3 style="margin-top: 30px;">Price Schedule</h3>
      <table class="data-table">
        <tr style="background-color: #f2f2f2;"><th>Qty</th><th>Description</th><th>Total Price (INR)</th></tr>
        <tr>
          <td>01</td>
          <td>Supply, Erection, Testing & Commissioning of {specs.get('car_travel')} Passenger Elevator as per specifications</td>
          <td><strong>Rs. {pricing.get('total_price', 913700):,.2f}</strong></td>
        </tr>
      </table>
      <p><strong>Amount in Words:</strong> {pricing.get('price_in_words', 'Rupees Nine Lakhs Thirteen Thousand Seven Hundred Only')}</p>
      <div class="sign-row" style="margin-top: 60px;">
        <div class="sign-line">Authorized Signatory</div>
        <div class="sign-line">Customer Signature</div>
      </div>
      <div class="page-break"></div>

      <!-- PAGE 6: PAYMENT & TERMS -->
      <div class="header">
        <div class="company-name">GUIDEX ELEVATOR PVT. LTD.</div>
        <div class="logo-box">▲ GUIDEX</div>
      </div>
      <h3>Payment Terms & Scope of Work</h3>
      <p><strong>Commercial Payment Schedule:</strong></p>
      <ul>
        <li><strong>20%</strong> On order confirmation & drawing sign-off.</li>
        <li><strong>70%</strong> On intimation of manufacturing completion (Dispatch in 4 weeks).</li>
        <li><strong>10%</strong> Before final commissioning and customer handover.</li>
      </ul>

      <p style="margin-top: 20px;"><strong>Client Civil / Site Scope:</strong></p>
      <ul>
        <li>Plumb shaft construction as per general arrangement dimensions ({specs.get('lift_well')}).</li>
        <li>Provision of safe scaffolding and locking storage for electricals.</li>
        <li>3-Phase AC 415V power switch at the top terminal and dual copper earthing.</li>
      </ul>
      <div class="page-break"></div>

      <!-- PAGE 7 & 8: BRANDS & WARRANTY -->
      <div class="header">
        <div class="company-name">GUIDEX ELEVATOR PVT. LTD.</div>
        <div class="logo-box">▲ GUIDEX</div>
      </div>
      <h3>Component Specifications & Brand Assurances</h3>
      <table class="data-table">
        <tr><th>Component</th><th>Grade / Make</th></tr>
        {"".join(f"<tr><td><strong>{b.get('parts')}</strong></td><td>{b.get('grade_brand')}</td></tr>" for b in brands)}
      </table>
      <p style="margin-top: 20px;"><strong>Warranty:</strong> 12 Months comprehensive warranty from the date of handover covering repair or replacement of defective manufacturing parts.</p>
      <div class="page-break"></div>

      <!-- PAGE 9: AMC AGREEMENT -->
      <div class="header">
        <div class="company-name">GUIDEX ELEVATOR PVT. LTD.</div>
        <div class="logo-box">▲ GUIDEX</div>
      </div>
      <h3>Annual Maintenance Contract (AMC / CMC)</h3>
      <table class="data-table">
        <tr><th>Year</th><th>Package</th><th>Routine Visits</th><th>Terms</th></tr>
        <tr>
          <td>1st & 2nd Year</td>
          <td>Comprehensive CMC</td>
          <td>8 Visits / Year</td>
          <td>Free (Safety Check, Lubrication, Tuning)</td>
        </tr>
      </table>
      <ul>
        <li>Emergency 24x7 priority assistance for passenger entrapment (mantrap rescues).</li>
        <li>Breakdown complaints attended within 24 hours of logging.</li>
      </ul>
      <div class="sign-row" style="margin-top: 80px;">
        <div class="sign-line">GUIDEX Service Executive</div>
        <div class="sign-line">Customer Signature & Seal</div>
      </div>

    </body>
    </html>
    """