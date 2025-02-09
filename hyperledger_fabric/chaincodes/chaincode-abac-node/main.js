const { Contract } = require('fabric-contract-api');
const ClientIdentity = require('fabric-shim').ClientIdentity;

'use strict';

class ABACChaincode extends Contract {
    // Initialize ledger with default users and assets
    async initLedger(ctx) {
        console.info('Ledger initialization');
        const users = [
            {
                userId: 'user1',
                role: 'superadmin',
                allowedTime: { start: '00:00', end: '23:59' },
                status: 'active',
                property_association: 'Global'
            }
        ];

        for (let user of users) {
            await ctx.stub.putState(user.userId, Buffer.from(JSON.stringify(user)));
            console.info('Added User', user);
        }
    }

    // Create a new user with specified attributes
    async createUser(ctx, userId, role, allowedStart, allowedEnd, status, property_association) {
        const cid = new ClientIdentity(ctx.stub);
        if (cid.getAttributeValue('abac.creator') !== 'true') {
            throw new Error('User does not have permission to create users');
        }
        
        const user = {
            userId,
            role,
            allowedTime: { start: allowedStart, end: allowedEnd },
            status,
            property_association
        };
        await ctx.stub.putState(userId, Buffer.from(JSON.stringify(user)));
        return JSON.stringify(user);
    }

    // Create a new asset with device attributes
    async createAsset(ctx, id, owner, deviceId, deviceType, deviceLocation, deviceStatus) {
        const cid = new ClientIdentity(ctx.stub);
        if (cid.getAttributeValue('abac.creator') !== 'true') {
            throw new Error('User does not have permission to create assets');
        }
        
        const asset = {
            id,
            owner,
            docType: 'asset',
            deviceAttributes: { deviceId, deviceType, deviceLocation, deviceStatus }
        };
        await ctx.stub.putState(id, Buffer.from(JSON.stringify(asset)));
        return JSON.stringify(asset);
    }

    // Access control function based on user and device attributes
    async accessAsset(ctx, assetId, userId, currentTime) {
        const assetJSON = await ctx.stub.getState(assetId);
        if (!assetJSON || assetJSON.length === 0) {
            throw new Error(`Asset with id ${assetId} does not exist`);
        }
        const asset = JSON.parse(assetJSON.toString());

        const userJSON = await ctx.stub.getState(userId);
        if (!userJSON || userJSON.length === 0) {
            throw new Error(`User with id ${userId} does not exist`);
        }
        const user = JSON.parse(userJSON.toString());

        if (user.status !== 'active') {
            throw new Error(`User ${userId} is not active`);
        }

        if (!this._isWithinAllowedTime(currentTime, user.allowedTime.start, user.allowedTime.end)) {
            throw new Error(`Access denied at ${currentTime}. Allowed time range: ${user.allowedTime.start}-${user.allowedTime.end}`);
        }

        return JSON.stringify({
            message: `Access granted for user ${userId} to asset ${assetId} at ${currentTime}`,
            asset,
            user
        });
    }

    // Helper method: Check if currentTime is within the allowed time range
    _isWithinAllowedTime(current, start, end) {
        const toMinutes = (timeStr) => {
            const [h, m] = timeStr.split(':').map(Number);
            return h * 60 + m;
        };
        return toMinutes(current) >= toMinutes(start) && toMinutes(current) <= toMinutes(end);
    }
}

module.exports = ABACChaincode;