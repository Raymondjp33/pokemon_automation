// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'catch.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CatchModel _$CatchModelFromJson(Map<String, dynamic> json) => CatchModel(
      encounters: (json['encounters'] as num?)?.toInt(),
      caughtTimestamp: json['caught_timestamp'] as num?,
      encounterMethod: json['encounter_method'] as String?,
      switchUsed: (json['switch'] as num?)?.toInt() ?? 1,
    );

Map<String, dynamic> _$CatchModelToJson(CatchModel instance) =>
    <String, dynamic>{
      'encounters': instance.encounters,
      'switch': instance.switchUsed,
      'encounter_method': instance.encounterMethod,
      'caught_timestamp': instance.caughtTimestamp,
    };
