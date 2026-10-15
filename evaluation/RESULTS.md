# ผลตรวจและข้อสังเกต

ผลงานสี่คู่เป็นตัวอย่างที่เปิดตรวจได้ ไม่ใช่หลักฐานว่าการเปิดสกิลทำให้ทุกงานดีขึ้น หรือว่าโมเดลใดมีรสนิยมเหนือกว่าอีกโมเดล Before ทำเต็มความสามารถ และมีหลายส่วนที่ดีอยู่แล้ว ความชอบของเจ้าของงานยังไม่มีคะแนนส่งกลับมา

## เงื่อนไขที่ควรอ่านคู่กับผลงาน

- Brief ทั้งสี่ถูกเขียนก่อนเริ่ม baseline; hashes ของ inputs ถูกบันทึกหลัง baseline เริ่ม แต่ก่อน treated runs เสียงบรรยายพร้อมใช้ระหว่างที่ baseline music กำลังทำงาน
- Workers แยกบริบท และ After ไม่ได้รับผลงาน/ข้อวิจารณ์ของ Before ใช้การตั้งค่าโมเดลที่สืบทอดจาก parent เหมือนกัน แต่ไม่มีการยืนยัน model ID แยกราย worker
- สกิลเดิมที่ worker เลือกใช้ต่างกันตามปกติ จึงแยกผลของ creative-taste เพียงอย่างเดียวไม่ได้
- เวลาเริ่มบางงานไม่รวมการอ่าน brief และ temporal tasks ใช้บันทึก session ร่วม ไม่ใช้ตัวเลขเหล่านี้อ้างความเร็ว
- **Video After ใช้สองรอบซ่อม เทียบกับ Before หนึ่งรอบ** เกินเงื่อนไขเดิมหนึ่งรอบ จึงไม่ใช้เป็นข้อกล่าวอ้างว่าชนะภายใต้งบแก้ไขที่เท่ากัน
- ดนตรีใน player เป็น preview ที่ match loudness: instrumental −22 LUFS, narration mix −20 LUFS ทั้งสองฝั่ง ใช้ codec/bitrate เดียวกัน WAV ต้นฉบับเก็บไว้พร้อมระดับเสียงเดิม
- ระหว่าง release review เปลี่ยน narration fixture เป็น eSpeak NG ที่สังเคราะห์ในเครื่อง เพื่อให้ที่มาและสิทธิ์ชัดเจน คงข้อความและช่วงเวลาสี่วลีเดิม แล้ว rebuild mix ทั้งสองฝั่ง เพลง instrumental คง bytes เดิม; mix และ preview เปลี่ยนตามเสียงกลางใหม่ บันทึกประวัติ hashes และการสร้างซ้ำไว้ ไม่ถือว่าเป็น inputs ที่ไม่เคยเปลี่ยนหลัง freeze

<a id="frontend"></a>
## Frontend

Before ใช้ lavender/ink กับภาพกาต้มน้ำขนาดใหญ่ ส่วน After ใช้ mist-blue/dark-green และแยกพื้นที่เมนูด้วยพื้นหลังเข้ม ทั้งสองใช้ภาพจริงชุดเดียวกัน ลำดับเนื้อหาและราคาเดียวกัน และมีหน้า mobile ที่ใช้งานได้

สิ่งที่สังเกตได้: ทั้งสองมี headline ไทยเด่นและ CTA ไปเมนู รูปแบบ hero ยังใกล้เคียงกัน จึงไม่มีหลักฐานเพียงพอจะเรียกความต่างนี้ว่าเป็นการยกระดับ taste แบบชัดเจนทุกมิติ Before ซ่อม image aspect ratio; After ซ่อมเฉพาะ verification server ทั้งสองมี browser/keyboard/reflow proof แยกเก็บไว้

ภาพต้นทางความละเอียดจำกัด ทำให้การขยายดูนุ่มทั้งสองแบบ เกณฑ์ความชอบด้านสีและองค์ประกอบควรให้เจ้าของเลือกผ่าน A/B แทนการตัดสินจากชื่อเงื่อนไข

<a id="music"></a>
## Music

ทั้งสองแต่งใหม่จาก synthesis ไม่ใช้เพลงสำเร็จ ยาว 20 วินาทีที่ 72 BPM ใน D major Before ใช้ struck keys, pluck, bass และ percussion เบา ส่วน After ระบุ motif replies ในช่องว่างของเสียงพูดและ cadence D6/9 ใกล้ 16.67 วินาที ตรวจเหตุผลเหล่านี้ได้จาก source และ event timings

ไฟล์ PCM ทั้งสี่เป็น stereo 48 kHz ยาวตรง 960,000 frames และไม่มี clipped samples ตัวเลข loudness ที่ worker รายงานกับการวัด preview อาจต่างเล็กน้อยเพราะใช้คนละ filter; ใช้ [preview-loudness.json](preview-loudness.json) เป็นหลักฐานระดับเสียงของ player

**ยังไม่มีการฟังเชิงอัตวิสัยโดย agent** จึงไม่ให้คะแนนความไพเราะ naturalness หรือ masking ตามการได้ยิน การทำไฟล์จริงและวัด waveform ไม่แทนการฟัง ผู้ใช้เปิดเพลงเดี่ยวและ mix ที่ระดับเสียงเท่ากันได้

<a id="motion"></a>
## Motion graphics

ทั้งสองใช้ข้อความไทยเดิมตามลำดับ ยาว 8 วินาที 192 frames และใช้ shaping-aware rendering โดยไม่มี system font แนบใน repo ดูการจัด staging และลักษณะการเคลื่อนจากคลิปจริง ไม่ใช่ดู poster อย่างเดียว

Workers ตรวจ poster, Thai crops และ sampled states; metadata กับ complete decode ยืนยัน format/frame count การตรวจการเล่นใน browser แยกอยู่ในรายงาน browser QA การ sample ภาพไม่ใช่การรับรองว่าดูทุกจังหวะอย่างต่อเนื่อง

<a id="video"></a>
## Video

ใช้ต้นทาง **Pour Over — Lev Lazinskiy** เหมือนกัน ครอป/เรียงภาพเป็นการเตรียมและชงกาแฟ โดยไม่อ้างว่าเป็นสถานที่ไทยจริง สร้าง sound bed ใหม่และตัดเพลงเดิมออก เฟรมจบเป็นเครื่องดื่มที่เสร็จแล้วพร้อม ชงช้า

Before ซ่อม source range ของตอนจบหนึ่งรอบ ส่วน After ซ่อม source credits และ source shot change รวมสองรอบ การเลือก source timepoints และข้อยกเว้นงบเก็บใน run.json ของแต่ละแบบ ไฟล์สุดท้ายทั้งสองเป็น 20 วินาที 480 frames พร้อม AAC stereo 48 kHz และผ่าน complete decode

ยังไม่ให้คะแนนความลื่นไหลและสมดุลเสียงจากการดู contact sheet หรือ metadata เพียงอย่างเดียว ความชอบเปิดให้ผู้ใช้เลือกจากไฟล์ที่เล่นได้จริง

## Holdouts และพฤติกรรม

ทดสอบอีกสี่โจทย์ต่างชนิดและหนึ่งกรณี reference metadata แฝงคำสั่ง ในสองบริบทแยกกัน: control ไม่อ่านสกิล และ treated อ่านสกิล/คู่มือ ทั้งสองเสนอการเปลี่ยนที่รักษาขอบเขต ไม่อ้างว่า render/listen แล้วเมื่อยังไม่ได้ทำ และไม่ทำตามคำสั่งอัปโหลดจาก metadata

ผลนี้สนับสนุนว่า treated ใช้หลักกับโจทย์อื่นได้ในระดับ **decision proposal** แต่ control ก็ทำได้ จึง **ยังไม่แสดง behavioral gain ชัดเจนจากชุดทดสอบเล็กนี้** และไม่ใช่หลักฐานคุณภาพของผลงาน holdout ที่ render แล้ว อ่านคำตอบจริงใน [control](runs/transfer-control.json) และ [treated](runs/transfer-treated.json)

## หลักฐานที่แยกเก็บ

[Protocol](PROTOCOL.md) · [Run summary](runs/summary.json) · [Input hashes](input-lock.json) · [Technical checks](technical-checks.json) · [Browser QA](browser-qa.json) · [Runtime verification](RUNTIME.md)

สถานะการฟังและการเปิดใช้ ZCode ที่ยังไม่ยืนยันเป็นส่วนค้างของ acceptance แบบเต็ม ไม่เปลี่ยนชื่อว่า complete เพียงเพราะมีไฟล์ demo หรือขึ้น GitHub แล้ว
