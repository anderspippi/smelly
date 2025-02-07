#!/usr/bin/env python
# License: GPLv3 Copyright: 2022, anders Goyal <anders at backbiter-no.net>


import os

from . import BaseTest


class TestCrypto(BaseTest):
    def test_elliptic_curve_data_exchange(self):
        from smelly.fast_data_types import AES256GCMDecrypt, AES256GCMEncrypt, CryptoError, EllipticCurveKey

        alice = EllipticCurveKey()
        bob = EllipticCurveKey()
        alice_secret = alice.derive_secret(bob.public)
        bob_secret = bob.derive_secret(alice.public)
        self.assertEqual(len(alice_secret), 32)
        self.assertEqual(len(bob_secret), 32)
        self.assertEqual(alice_secret, bob_secret)

        auth_data = os.urandom(213)
        plaintext = os.urandom(1011)
        e = AES256GCMEncrypt(alice_secret)
        e.add_authenticated_but_unencrypted_data(auth_data)
        ciphertext = e.add_data_to_be_encrypted(plaintext, True)

        d = AES256GCMDecrypt(bob_secret, e.iv, e.tag)
        d.add_data_to_be_authenticated_but_not_decrypted(auth_data)
        q = d.add_data_to_be_decrypted(ciphertext, True)
        self.ae(q, plaintext)

        def corrupt_data(data):
            b = bytearray(data)
            b[0] = (b[0] + 13) % 256
            return bytes(b)

        d = AES256GCMDecrypt(bob_secret, e.iv, corrupt_data(e.tag))
        d.add_data_to_be_authenticated_but_not_decrypted(auth_data)
        self.assertRaises(
            CryptoError, d.add_data_to_be_decrypted, ciphertext, True)

        d = AES256GCMDecrypt(bob_secret, e.iv, e.tag)
        d.add_data_to_be_authenticated_but_not_decrypted(
            corrupt_data(
                auth_data))
        self.assertRaises(
            CryptoError, d.add_data_to_be_decrypted, ciphertext, True)

        d = AES256GCMDecrypt(bob_secret, e.iv, e.tag)
        d.add_data_to_be_authenticated_but_not_decrypted(auth_data)
        self.assertRaises(CryptoError, d.add_data_to_be_decrypted,
                          corrupt_data(ciphertext), True)
