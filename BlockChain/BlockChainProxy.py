from web3 import Web3

class EthereumProxy(object):

    def __init__(self, infura_url, abi, address):
        self.web3 = Web3(Web3.HTTPProvider(infura_url))
        self.contract = self.web3.eth.contract(address=address, abi=abi)

    """
        输入为编码后的numpy一维数组,返回值是一个List，List中每一个元素是一个tuple，tuple第一个nationalId，第二个是feature的string
    """
    def getCandidateList(self, face_code):
        code_str = ""
        for code_char in face_code:
            code_str += str(code_char)

        print(code_str)
        candidate_list = self.contract.functions.getCandidatesFromFacialHash(code_str).call()
        return candidate_list

    """
        nationalId是字符串，根据nationalId返回公民的所有身份信息
    """
    def getCivilianInfoByNationalId(self, nationalId):
        civilianInfo = self.contract.functions.getAllDataByNationalID(nationalId).call()
        return civilianInfo

    """
        向区块链中插入用户信息
    """
    def insertUserinfo(self, userinfo):
        # Initialize the address calling the functions/signing transactions
        caller = "0x7B47005C466F0f00C53f748b1Edc7278b9AFcD1c"
        private_key = "1a29cb34d5a17d4405b418b13891ac02c82b32b3aa9f0752f3b50369a38b7228"  # To sign the transaction
        # initialize the chain id, we need it to build the transaction for replay protection
        chain_id = 11155111  # Sepolia test network

        # Initialize address nonce
        #nonce = self.web3.eth.get_transaction_count(caller)
        nonce = self.web3.eth.getTransactionCount(caller)

        # Call your function
        call_function = self.contract.functions.newIdentity(
            userinfo[0],  # nationalID
            userinfo[1],  # name
            userinfo[2],  # millitaryClearance
            userinfo[3],  # gender
            userinfo[4],  # facialFeatures
            userinfo[5]  # facialHash
        ).buildTransaction({"chainId": chain_id, "from": caller, "nonce": nonce})

        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(call_function, private_key=private_key)

        # Send transaction
        #send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        send_tx = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        # Wait for transaction receipt
        #tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        tx_receipt = self.web3.eth.waitForTransactionReceipt(send_tx)
        print(tx_receipt)  # Optional

    """
        让区块链返回所有feature信息,是一个list，list中每个元素是一个tuple(nationalID, feature)
    """
    def getAllFeatureList(self):
        feature_list = self.contract.functions.getAllFacialFeaturesAndNationalID().call()
        return feature_list


    def test(self):
        infura_url = "https://sepolia.infura.io/v3/71199b1f00e74f1194a09255d9ce0d44"
        web3 = Web3(Web3.HTTPProvider(infura_url))

        # https://sepolia.etherscan.io/address/0x68a53755ab9155713b9c77a2fa8c8c6cbb8a1c07#readContract
        abi = [{"inputs": [{"internalType": "string", "name": "nationalID", "type": "string"}],
                "name": "destroyIdentityByNationalID", "outputs": [], "stateMutability": "nonpayable",
                "type": "function"}, {"inputs": [{"internalType": "string", "name": "nationalID", "type": "string"}],
                                      "name": "getAllInfoByNationalID", "outputs": [{"components": [
                {"internalType": "string", "name": "nationalID", "type": "string"},
                {"internalType": "string", "name": "name", "type": "string"},
                {"internalType": "enum Identity.ClearanceLevel", "name": "millitaryClearance", "type": "uint8"},
                {"internalType": "enum Identity.Gender", "name": "gender", "type": "uint8"},
                {"internalType": "string", "name": "facialHash", "type": "string"},
                {"internalType": "string", "name": "facialFeatures", "type": "string"}],
                                                                                     "internalType": "struct Identity.IdentityInfo",
                                                                                     "name": "", "type": "tuple"}],
                                      "stateMutability": "view", "type": "function"},
               {"inputs": [{"internalType": "string", "name": "facialHash", "type": "string"}],
                "name": "getCandidatesFromFacialHash", "outputs": [{"components": [
                   {"internalType": "string", "name": "nationalID", "type": "string"},
                   {"internalType": "string", "name": "facialFeatures", "type": "string"}],
                                                                    "internalType": "struct Identity.Candidate[]",
                                                                    "name": "", "type": "tuple[]"}],
                "stateMutability": "view", "type": "function"},
               {"inputs": [{"internalType": "string", "name": "nationalID", "type": "string"}],
                "name": "getFacialFeaturesByNationalID",
                "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view",
                "type": "function"}, {"inputs": [{"internalType": "string", "name": "nationalID", "type": "string"}],
                                      "name": "getGenderByNationalID", "outputs": [
                    {"internalType": "enum Identity.Gender", "name": "", "type": "uint8"}], "stateMutability": "view",
                                      "type": "function"},
               {"inputs": [{"internalType": "string", "name": "nationalID", "type": "string"}],
                "name": "getMillitaryClearanceByNationalID",
                "outputs": [{"internalType": "enum Identity.ClearanceLevel", "name": "", "type": "uint8"}],
                "stateMutability": "view", "type": "function"},
               {"inputs": [{"internalType": "string", "name": "nationalID", "type": "string"}],
                "name": "getNameByNationalID", "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                "stateMutability": "view", "type": "function"}, {
                   "inputs": [{"internalType": "string", "name": "nationalID", "type": "string"},
                              {"internalType": "string", "name": "name", "type": "string"},
                              {"internalType": "enum Identity.ClearanceLevel", "name": "millitaryClearance",
                               "type": "uint8"},
                              {"internalType": "enum Identity.Gender", "name": "gender", "type": "uint8"},
                              {"internalType": "string", "name": "facialFeatures", "type": "string"},
                              {"internalType": "string", "name": "facialHash", "type": "string"}],
                   "name": "newIdentity", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]

        # Initialize the address calling the functions/signing transactions
        caller = "0x7B47005C466F0f00C53f748b1Edc7278b9AFcD1c"
        private_key = "1a29cb34d5a17d4405b418b13891ac02c82b32b3aa9f0752f3b50369a38b7228"  # To sign the transaction

        contract_address = "0xF3801F00d35fE4DaF1d3e80645F8765799D6b77E"
        contract = web3.eth.contract(address=contract_address, abi=abi)

        # initialize the chain id, we need it to build the transaction for replay protection
        chain_id = 11155111  # Sepolia test network

        # Initialize address nonce
        nonce = web3.eth.get_transaction_count(caller)

        # Call your function
        call_function = contract.functions.newIdentity(
            "10",  # nationalID
            "Hello",  # name
            1,  # millitaryClearance
            1,  # gender
            "feature10",  # facialFeatures
            "hash10"  # facialHash
        ).build_transaction({"chainId": chain_id, "from": caller, "nonce": nonce})

        # Sign transaction
        signed_tx = web3.eth.account.sign_transaction(call_function, private_key=private_key)

        # Send transaction
        send_tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(send_tx)
        print(tx_receipt)  # Optional

        # print(contract.functions.getCandidatesFromFacialHash('1').call())

#face_code = np.array([0])
#candidate_list = getCandidateList(face_code)
#rint(candidate_list)
#print(getCivilianInfoByNationalId("1"))
