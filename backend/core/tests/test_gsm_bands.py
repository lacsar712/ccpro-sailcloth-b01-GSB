"""克重色带分界专页验收测试。

覆盖：
- 登录即可读（操作工也能看），仅管理员可写
- 保存后读取仍是新分界（不退回出厂值）
- 后写成功的一版覆盖先写，库里只留一版
- 改分界不触碰任何布卷的状态与克重
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import ClothRoll, GsmBandSettings, Loft

User = get_user_model()

URL = "/api/gsm-bands/"


class GsmBandSettingsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="boss", password="x", role=User.ROLE_ADMIN
        )
        self.admin2 = User.objects.create_user(
            username="boss2", password="x", role=User.ROLE_ADMIN
        )
        self.worker = User.objects.create_user(
            username="hand", password="x", role=User.ROLE_WORKER
        )
        loft = Loft.objects.create(name="北岸帆布间")
        self.roll = ClothRoll.objects.create(
            loft=loft,
            roll_code="R-01",
            status=ClothRoll.STATUS_DIPPING,
            fabric_weight_gsm=420,
        )

    def auth(self, user):
        self.client.force_authenticate(user)

    def test_defaults_seeded_and_readable_by_worker(self):
        self.auth(self.worker)
        res = self.client.get(URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["lightMax"], 400)
        self.assertEqual(res.data["heavyMin"], 440)

    def test_anonymous_cannot_read(self):
        res = self.client.get(URL)
        self.assertEqual(res.status_code, 401)

    def test_worker_cannot_write(self):
        self.auth(self.worker)
        res = self.client.put(URL, {"lightMax": 300, "heavyMin": 500}, format="json")
        self.assertEqual(res.status_code, 403)
        solo = GsmBandSettings.get_solo()
        self.assertEqual((solo.light_max, solo.heavy_min), (400, 440))

    def test_admin_write_persists(self):
        self.auth(self.admin)
        res = self.client.put(URL, {"lightMax": 350, "heavyMin": 460}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["updatedBy"], "boss")
        # 重新读取（模拟刷新/换间再回来）仍是新分界
        res = self.client.get(URL)
        self.assertEqual((res.data["lightMax"], res.data["heavyMin"]), (350, 460))

    def test_last_successful_write_wins_single_row(self):
        # 两名主管交叉提交：库里只留后写成功的那一版
        self.auth(self.admin)
        self.client.put(URL, {"lightMax": 300, "heavyMin": 500}, format="json")
        self.auth(self.admin2)
        res = self.client.put(URL, {"lightMax": 320, "heavyMin": 480}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(GsmBandSettings.objects.count(), 1)
        solo = GsmBandSettings.get_solo()
        self.assertEqual((solo.light_max, solo.heavy_min), (320, 480))
        self.assertEqual(solo.updated_by, self.admin2)

    def test_reject_inverted_and_non_integer(self):
        self.auth(self.admin)
        res = self.client.put(URL, {"lightMax": 500, "heavyMin": 300}, format="json")
        self.assertEqual(res.status_code, 400)
        res = self.client.put(URL, {"lightMax": 399.5, "heavyMin": 500}, format="json")
        self.assertEqual(res.status_code, 400)
        solo = GsmBandSettings.get_solo()
        self.assertEqual((solo.light_max, solo.heavy_min), (400, 440))

    def test_write_does_not_touch_rolls(self):
        before_status = self.roll.status
        before_gsm = self.roll.fabric_weight_gsm
        self.auth(self.admin)
        res = self.client.put(URL, {"lightMax": 360, "heavyMin": 470}, format="json")
        self.assertEqual(res.status_code, 200)
        self.roll.refresh_from_db()
        self.assertEqual(self.roll.status, before_status)
        self.assertEqual(self.roll.fabric_weight_gsm, before_gsm)

    def test_band_for_boundaries(self):
        solo = GsmBandSettings.get_solo()
        self.assertEqual(solo.band_for(399), GsmBandSettings.BAND_LIGHT)
        self.assertEqual(solo.band_for(400), GsmBandSettings.BAND_LIGHT)
        self.assertEqual(solo.band_for(401), GsmBandSettings.BAND_MEDIUM)
        self.assertEqual(solo.band_for(439), GsmBandSettings.BAND_MEDIUM)
        self.assertEqual(solo.band_for(440), GsmBandSettings.BAND_HEAVY)
        self.assertEqual(solo.band_for(600), GsmBandSettings.BAND_HEAVY)
